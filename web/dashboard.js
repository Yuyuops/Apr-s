const INDICATORS = [
  {id:"gdp", label:"Richesse produite", short:"PIB", group:"Économie", variables:["PIB"], kind:"money"},
  {id:"employment", label:"Emploi", short:"Emploi", group:"Économie", variables:["emploi","emploi_seniors","population_active"], kind:"generic"},
  {id:"purchasing_power", label:"Pouvoir d'achat", short:"Pouvoir d'achat", group:"Économie", variables:["revenu_disponible","revenu_menages","salaires","pauvrete","consommation"], kind:"generic"},
  {id:"prices", label:"Prix", short:"Prix / inflation", group:"Économie", variables:["inflation","prix_energie","prix_logement","loyers"], kind:"generic"},

  {id:"spending", label:"Dépenses publiques", short:"Dépenses", group:"Finances publiques", variables:["depenses_publiques"], kind:"money"},
  {id:"revenue", label:"Recettes publiques", short:"Recettes", group:"Finances publiques", variables:["recettes_publiques","cotisations"], kind:"money"},
  {id:"deficit", label:"Déficit public", short:"Déficit", group:"Finances publiques", variables:["deficit","finances_publiques","budget_public"], kind:"money"},
  {id:"debt", label:"Dette publique", short:"Dette", group:"Finances publiques", variables:["dette"], kind:"percent_gdp"},

  {id:"health", label:"Santé", short:"Santé", group:"Services & société", variables:["capacite_soins","temps_acces","depenses_sante"], kind:"generic"},
  {id:"education", label:"Éducation", short:"Éducation", group:"Services & société", variables:["taille_classes","depenses_education"], kind:"generic"},
  {id:"security", label:"Sécurité & justice", short:"Sécurité / justice", group:"Services & société", variables:["effectifs_police","depenses_securite","capacite_operationnelle","delais_justice","stock_affaires","capacite_justice"], kind:"generic"},
  {id:"housing", label:"Logement", short:"Logement", group:"Services & société", variables:["logement","offre_logement","prix_logement","loyers"], kind:"generic"},
  {id:"mobility", label:"Transports & infrastructures", short:"Transports", group:"Services & société", variables:["mobilite","investissement_public"], kind:"generic"},

  {id:"energy", label:"Énergie & climat", short:"Énergie / climat", group:"Transition & institutions", variables:["mix_energetique","prix_energie","emissions_CO2","pollution","investissement"], kind:"generic"},
  {id:"institutions", label:"Institutions & international", short:"Institutions", group:"Transition & institutions", variables:["organisation_etat","competences","institutions","frontieres","relations_internationales","reglementation","calendrier_legislatif"], kind:"generic"}
];

const STRUCTURAL_TARGETS = new Set([
  "administrative_layer","administrative_reorganisation","eu_exit","euro_exit",
  "nato_exit","treaty_or_eu_rule","constitutional_reform","foreign_policy"
]);

function money(v){
  if(v==null) return null;
  const abs=Math.abs(v);
  if(abs>=1e12) return (v/1e12).toLocaleString("fr-FR",{maximumFractionDigits:2})+" T€";
  if(abs>=1e9) return (v/1e9).toLocaleString("fr-FR",{maximumFractionDigits:1})+" Md€";
  if(abs>=1e6) return (v/1e6).toLocaleString("fr-FR",{maximumFractionDigits:1})+" M€";
  return v.toLocaleString("fr-FR",{maximumFractionDigits:0})+" €";
}

function signedMoney(v){
  if(v==null) return null;
  const sign=v>0?"+":v<0?"−":"";
  return sign+money(Math.abs(v));
}

function signedPoints(v){
  if(v==null) return null;
  const sign=v>0?"+":v<0?"−":"";
  return sign+Math.abs(v).toLocaleString("fr-FR",{maximumFractionDigits:3})+" pt de PIB";
}

function isAffected(indicator,affected){
  return indicator.variables.some(v=>affected.has(v));
}

function linearSeries(start,end,steps=7){
  return Array.from({length:steps},(_,i)=>start+(end-start)*(i/(steps-1)));
}

function formatOperational(effect){
  const sign=effect.value>0?"+":effect.value<0?"−":"";
  const value=Math.abs(effect.value).toLocaleString("fr-FR",{maximumFractionDigits:2});
  return sign+value+" "+effect.unit;
}

export function buildDashboardState({policies,simulation,fiscal,baseline,hypotheses,operationalEffects=[]}){
  const affected=new Set(hypotheses.affectedVariables||[]);
  const structural=policies.some(p=>STRUCTURAL_TARGETS.has(p.target));
  const operationalByIndicator=operationalEffects.reduce((acc,effect)=>{
    (acc[effect.indicator] ||= []).push(effect);
    return acc;
  },{});
  const annualSpending=simulation.directEffects.annual_public_spending_delta_eur||0;
  const annualRevenue=simulation.directEffects.annual_public_revenue_delta_eur||0;
  const baselineRevenue=baseline.gdp_eur*(baseline.public_revenue_pct_gdp/100);

  const states=INDICATORS.map(indicator=>{
    const touched=isAffected(indicator,affected);
    const base={
      ...indicator,
      baseline:null,
      projected:null,
      delta:null,
      status:touched?"affected_unmodelled":"unchanged_unknown",
      detail:touched?"Cette mesure peut agir sur cet indicateur, mais le modèle chiffré n'est pas encore connecté.":"Aucun effet calculé pour les mesures saisies.",
      confidence:touched?"À modéliser":"Non affecté directement",
      trend:null,
      trendLabel:null
    };

    const directOperational=operationalByIndicator[indicator.id]||[];
    if(directOperational.length){
      base.status="calculated";
      base.baseline="Situation actuelle";
      base.projected="Capacité modifiée";
      base.delta=directOperational.map(formatOperational).join(" · ");
      base.detail=directOperational.map(x=>x.label).join(" · ")+" — quantité explicitement annoncée. L'effet sur les résultats du service reste à modéliser.";
      base.confidence="Calcul direct";
      return base;
    }

    if(indicator.id==="gdp"){
      base.baseline=money(baseline.gdp_eur);
      base.projected=money(baseline.gdp_eur);
      base.detail=touched?"PIB de départ connu. L'effet de la mesure attend le modèle macroéconomique.":"Aucun effet sur le PIB n'est calculé pour ce paquet.";
      return base;
    }

    if(indicator.id==="spending"){
      base.baseline=money(baseline.public_expenditure_eur);
      base.projected=money(baseline.public_expenditure_eur+annualSpending);
      base.delta=signedMoney(annualSpending);
      base.status=annualSpending!==0?"calculated":base.status;
      base.detail=annualSpending!==0?"Variation annuelle directement calculable.":"Aucune variation annuelle de dépense directement calculée.";
      base.confidence=annualSpending!==0?"Calcul direct":"À modéliser";
      if(annualSpending!==0){
        const cumulative=annualSpending*simulation.horizonMonths/12;
        base.trend=linearSeries(0,cumulative);
        base.trendLabel="Impact cumulé";
      }
      return base;
    }

    if(indicator.id==="revenue"){
      base.baseline=money(baselineRevenue);
      base.projected=money(baselineRevenue+annualRevenue);
      base.delta=signedMoney(annualRevenue);
      base.status=annualRevenue!==0?"calculated":base.status;
      base.detail=annualRevenue!==0?"Variation annuelle directement calculable.":"Aucune variation annuelle de recette directement calculée.";
      base.confidence=annualRevenue!==0?"Calcul direct":"À modéliser";
      if(annualRevenue!==0){
        const cumulative=annualRevenue*simulation.horizonMonths/12;
        base.trend=linearSeries(0,cumulative);
        base.trendLabel="Impact cumulé";
      }
      return base;
    }

    if(indicator.id==="deficit"){
      base.baseline=money(baseline.public_deficit_eur);
      if(fiscal){
        base.projected=money(fiscal.annualPublicDeficitAfterDirectEffectEur);
        base.delta=signedMoney(fiscal.cumulativePublicDeficitDeltaEur);
        base.status="calculated";
        base.detail="Le chiffre principal est le déficit annuel après effet direct ; la variation affichée est cumulée jusqu'à l'horizon.";
        base.confidence="Calcul direct";
        base.trend=linearSeries(0,fiscal.cumulativePublicDeficitDeltaEur);
        base.trendLabel="Déficit cumulé ajouté";
      } else {
        base.projected=base.baseline;
      }
      return base;
    }

    if(indicator.id==="debt"){
      base.baseline=baseline.public_debt_pct_gdp.toLocaleString("fr-FR",{maximumFractionDigits:1})+" % du PIB";
      if(fiscal){
        const projected=baseline.public_debt_pct_gdp+fiscal.cumulativeDebtImpactPctGdp;
        base.projected=projected.toLocaleString("fr-FR",{maximumFractionDigits:2})+" % du PIB";
        base.delta=signedPoints(fiscal.cumulativeDebtImpactPctGdp);
        base.status="calculated";
        base.detail="Effet comptable cumulé du paquet sur la dette, à PIB inchangé.";
        base.confidence="Calcul direct";
        base.trend=linearSeries(baseline.public_debt_pct_gdp,projected);
        base.trendLabel="Dette projetée";
      } else {
        base.projected=base.baseline;
      }
      return base;
    }

    if(indicator.id==="institutions" && structural){
      base.status="scenario";
      base.baseline="Situation actuelle";
      base.projected="Scénarios à comparer";
      base.delta="Structure modifiée";
      base.detail="La mesure change des règles, institutions ou relations internationales : plusieurs scénarios doivent être comparés.";
      base.confidence="Scénarios";
      return base;
    }

    return base;
  });

  const calculated=states.filter(x=>x.status==="calculated").length;
  const pending=states.filter(x=>x.status==="affected_unmodelled").length;
  const scenarios=states.filter(x=>x.status==="scenario").length;

  return {indicators:states,summary:{calculated,pending,scenarios}};
}

export function groupDashboardIndicators(indicators){
  return indicators.reduce((acc,item)=>{
    (acc[item.group] ||= []).push(item);
    return acc;
  },{});
}
