import {applyFiscalBaseline,compilePolicy,simulateProgram} from "./engine.js";
import {hypothesisSummary} from "./hypotheses.js";
import {buildDashboardState,groupDashboardIndicators} from "./dashboard.js";
import {detectMeasureType,MEASURE_TYPES} from "./measure-types.js";
import {buildDirectParameterChanges,fetchSmicHourly} from "./openfisca.js";
import {
  ACTION_LABELS,
  CONFIDENCE_LABELS,
  EVIDENCE_LABELS,
  EXOGENOUS_LABELS,
  MODEL_LABELS,
  SCENARIO_LABELS,
  SOURCE_STATUS_LABELS,
  TARGET_LABELS,
  UNCERTAINTY_LABELS,
  VARIABLE_LABELS,
  humanize
} from "./labels.js";

const measure=document.querySelector("#measure");
const preset=document.querySelector("#preset");
const horizon=document.querySelector("#horizon");
const horizonLabel=document.querySelector("#horizonLabel");
const result=document.querySelector("#result");
const sourceBox=document.querySelector("#sourceBox");
const baselineBox=document.querySelector("#baseline");
const measureCount=document.querySelector("#measureCount");
const resetButton=document.querySelector("#resetButton");
const horizonButtons=[...document.querySelectorAll("#horizonButtons button")];

const [presets,baseline,hypothesisRegistry,smicHourly]=await Promise.all([
  fetch("./demo-policies.json").then(r=>r.json()),
  fetch("./france_2025.json").then(r=>r.json()),
  fetch("./hypotheses_registry.json").then(r=>r.json()),
  fetchSmicHourly().catch(()=>null)
]);
const referenceData={smicHourly};

for(const p of presets){
  const o=document.createElement("option");
  o.value=p.id;
  o.textContent=p.label;
  preset.appendChild(o);
}

baselineBox.innerHTML=
  '<div class="baseline-head"><div><span class="eyebrow">POINT DE DÉPART OFFICIEL</span><h2>France '+baseline.period+'</h2></div>'+
  '<div class="baseline-source">Données Insee · mises à jour le '+baseline.retrieved_at+'</div></div>'+
  '<div class="baseline-grid">'+
    '<div><span>Richesse produite (PIB)</span><strong>'+formatBn(baseline.gdp_eur)+'</strong></div>'+
    '<div><span>Dépenses publiques</span><strong>'+formatBn(baseline.public_expenditure_eur)+'</strong></div>'+
    '<div><span>Déficit public</span><strong>'+formatBn(baseline.public_deficit_eur)+' · '+baseline.public_deficit_pct_gdp+' % du PIB</strong></div>'+
    '<div><span>Dette publique</span><strong>'+baseline.public_debt_pct_gdp+' % du PIB</strong></div>'+
    (smicHourly?'<div><span>SMIC horaire brut</span><strong>'+smicHourly.value.toLocaleString("fr-FR",{minimumFractionDigits:2,maximumFractionDigits:2})+' €/h</strong><small>OpenFisca · '+smicHourly.effectiveDate+'</small></div>':"")+
  '</div>';

preset.addEventListener("change",()=>{
  const p=presets.find(x=>x.id===preset.value);
  if(!p) return;
  measure.value=p.text;
  if(p.source){
    const status=SOURCE_STATUS_LABELS[p.status]||"source indiquée";
    sourceBox.innerHTML='Source : <a href="'+p.source+'" target="_blank" rel="noreferrer">voir le document</a> · '+status;
  } else {
    sourceBox.textContent="Exemple fictif pour tester le simulateur.";
  }
  render();
});

measure.addEventListener("input",()=>{
  preset.value="";
  sourceBox.textContent="Texte saisi librement : aucune source politique n'est attribuée.";
  render();
});
horizon.addEventListener("input",render);
horizonButtons.forEach(button=>button.addEventListener("click",()=>{
  horizon.value=button.dataset.months;
  render();
}));
resetButton.addEventListener("click",()=>{
  preset.value=presets[0]?.id||"";
  const selected=presets[0];
  measure.value=selected?.text||"";
  sourceBox.textContent=selected?.source?"Source officielle chargée.":"Exemple fictif pour tester le simulateur.";
  horizon.value="12";
  render();
});

function formatBn(v){
  return (v/1e9).toLocaleString("fr-FR",{maximumFractionDigits:1})+" Md€";
}

function eur(v){
  const abs=Math.abs(v);
  const sign=v<0?"−":"+";
  if(abs>=1e9) return sign+(abs/1e9).toFixed(2)+" Md€";
  if(abs>=1e6) return sign+(abs/1e6).toFixed(2)+" M€";
  return sign+abs.toLocaleString("fr-FR")+" €";
}

function tag(s){return '<span class="tag">'+s+"</span>";}

function tags(values,dictionary){
  return values.map(v=>tag(humanize(v,dictionary))).join(" ");
}

function horizonText(months){
  return months===1?"1 mois":months===6?"6 mois":months===12?"1 an":months===24?"2 ans":months===60?"5 ans":months+" mois";
}

function sparkline(points){
  if(!points || points.length<2) return "";
  const width=180, height=42, pad=3;
  const min=Math.min(...points), max=Math.max(...points);
  const span=(max-min)||1;
  const coords=points.map((value,index)=>{
    const x=pad+(width-2*pad)*(index/(points.length-1));
    const y=height-pad-(height-2*pad)*((value-min)/span);
    return x.toFixed(1)+","+y.toFixed(1);
  }).join(" ");
  return '<svg class="sparkline" viewBox="0 0 '+width+' '+height+'" role="img" aria-label="Évolution dans le temps"><polyline points="'+coords+'" fill="none" stroke="currentColor" stroke-width="2.5" vector-effect="non-scaling-stroke"/></svg>';
}

function directLabel(key){
  return ({
    annual_public_spending_delta_eur:"Dépenses publiques — par an",
    cumulative_public_spending_delta_eur:"Dépenses publiques — cumulées",
    annual_public_revenue_delta_eur:"Recettes publiques — par an",
    cumulative_public_revenue_delta_eur:"Recettes publiques — cumulées"
  })[key]||key;
}

function render(){
  const months=Number(horizon.value);
  const horizonName=horizonText(months);
  horizonLabel.textContent=horizonName;

  const texts=measure.value.split(/\n+/).map(x=>x.trim()).filter(Boolean);
  const policies=texts.map(text=>{
    const policy=compilePolicy(text);
    policy.measureType=detectMeasureType(policy);
    return policy;
  });
  measureCount.textContent=policies.length+" mesure"+(policies.length>1?"s":"")+" analysée"+(policies.length>1?"s":"");
  horizonButtons.forEach(button=>button.classList.toggle("active",Number(button.dataset.months)===months));
  const simulation=simulateProgram(policies,months);
  const fiscal=applyFiscalBaseline(simulation,baseline);
  const hypotheses=hypothesisSummary(policies,hypothesisRegistry,months);
  const dashboard=buildDashboardState({policies,simulation,fiscal,baseline,hypotheses});
  const dashboardGroups=groupDashboardIndicators(dashboard.indicators);
  const directParameterChanges=buildDirectParameterChanges(policies,referenceData);

  const dashboardGroupsHtml=Object.entries(dashboardGroups).map(([group,items])=>{
    const cards=items.map(item=>{
      const delta=item.delta
        ? '<div class="sim-delta">'+item.delta+'</div>'
        : item.status==="affected_unmodelled"
          ? '<div class="sim-pending">Impact à calculer</div>'
          : item.status==="scenario"
            ? '<div class="sim-scenario">Plusieurs scénarios</div>'
            : '<div class="sim-neutral">Pas d’effet chiffré</div>';

      const values=item.baseline
        ? '<div class="sim-values"><span>'+item.baseline+'</span><span class="sim-arrow">→</span><strong>'+(item.projected||item.baseline)+'</strong></div>'
        : '<div class="sim-values"><span>Valeur de départ à connecter</span></div>';

      const trend=item.trend
        ? '<div class="trend-block"><span>'+item.trendLabel+'</span>'+sparkline(item.trend)+'</div>'
        : "";

      return '<article class="sim-card sim-'+item.status+'">'+
        '<div class="sim-card-head"><span>'+item.label+'</span><small>'+item.confidence+'</small></div>'+
        values+
        delta+
        trend+
        '<p>'+item.detail+'</p>'+
      '</article>';
    }).join("");

    return '<section class="sim-group"><h3>'+group+'</h3><div class="sim-cards">'+cards+'</div></section>';
  }).join("");

  const directParameterHtml=directParameterChanges.length
    ? '<section class="direct-params"><h3>Paramètres modifiés directement</h3>'+
      directParameterChanges.map(change=>{
        const delta=change.delta>=0?"+"+change.delta.toFixed(2):change.delta.toFixed(2);
        const pct=change.deltaPct>=0?"+"+change.deltaPct.toFixed(1):change.deltaPct.toFixed(1);
        return '<article class="param-card">'+
          '<div><span>'+change.label+'</span><small>'+change.confidence+'</small></div>'+
          '<div class="param-values"><strong>'+change.baseline.toFixed(2)+' '+change.unit+'</strong><span>→</span><strong>'+change.projected.toFixed(2)+' '+change.unit+'</strong></div>'+
          '<p>Variation : <b>'+delta+' '+change.unit+'</b> ('+pct+' %)</p>'+
          '<p class="source">Valeur de départ : <a href="'+change.sourceUrl+'" target="_blank" rel="noreferrer">'+change.sourceLabel+'</a> · applicable depuis '+change.effectiveDate+'</p>'+
        '</article>';
      }).join("")+
    '</section>'
    : "";

  const measureTypeBadges=[...new Set(policies.map(p=>p.measureType))].map(type=>{
    const meta=MEASURE_TYPES[type];
    return meta?'<span class="type-badge" title="'+meta.effect+'">'+meta.label+'</span>':"";
  }).join("");

  const dashboardHtml=
    '<section class="sim-dashboard">'+
      '<div class="sim-dashboard-head">'+
        '<div><span class="eyebrow">FRANCE À '+horizonName.toUpperCase()+'</span><h2>Tableau de bord des impacts</h2></div>'+
        '<div class="sim-summary">'+
          '<div><strong>'+dashboard.summary.calculated+'</strong><span>indicateurs calculés</span></div>'+
          '<div><strong>'+dashboard.summary.pending+'</strong><span>touchés, à modéliser</span></div>'+
          '<div><strong>'+dashboard.summary.scenarios+'</strong><span>en scénarios</span></div>'+
        '</div>'+
      '</div>'+
      '<p class="sim-intro">Comme dans SimCity : le programme modifie l’état de la France. Les cartes chiffrées bougent avec le temps ; les cartes en attente montrent où un modèle fiable manque encore.</p>'+
      '<div class="type-badges">'+measureTypeBadges+'</div>'+
      directParameterHtml+
      dashboardGroupsHtml+
    '</section>';

  const classifications=policies.map((p,i)=>{
    const type=MEASURE_TYPES[p.measureType];
    return "<li><strong>"+(i+1)+". "+humanize(p.target,TARGET_LABELS)+"</strong> · "+humanize(p.action,ACTION_LABELS)+
      (type?" · <span>"+type.label+"</span>":"")+"</li>";
  }).join("")||"<li>Aucune mesure saisie.</li>";

  const direct=Object.entries(simulation.directEffects)
    .map(([key,value])=>"<li><span>"+directLabel(key)+"</span> : <strong>"+eur(value)+"</strong></li>")
    .join("")||"<li>Rien n'est encore calculable directement avec les informations fournies.</li>";

  const missingCalculations=simulation.missingCapabilities.length
    ? tags(simulation.missingCapabilities,MODEL_LABELS)
    : '<span class="muted">Rien ne manque pour les calculs directs affichés.</span>';

  const notes=[...simulation.scenarioNotes,...simulation.assumptions]
    .map(x=>"<li>"+x+"</li>").join("")||"<li>Aucune remarque particulière.</li>";

  const fiscalHtml=fiscal?
    '<section class="fiscal-impact"><h3>Effet budgétaire à '+horizonName+'</h3>'+
      '<div class="impact-primary"><span>Déficit supplémentaire cumulé</span><strong>'+eur(fiscal.cumulativePublicDeficitDeltaEur)+'</strong></div>'+
      '<div class="impact-grid">'+
        '<div><span>Dépenses cumulées</span><strong>'+eur(fiscal.cumulativePublicSpendingDeltaEur)+'</strong></div>'+
        '<div><span>Recettes cumulées</span><strong>'+eur(fiscal.cumulativePublicRevenueDeltaEur)+'</strong></div>'+
        '<div><span>Effet cumulé sur la dette</span><strong>'+((fiscal.cumulativeDebtImpactPctGdp>=0?"+":"")+fiscal.cumulativeDebtImpactPctGdp.toFixed(3))+' point de PIB</strong></div>'+
        '<div><span>Effet sur le déficit par an</span><strong>'+eur(fiscal.annualPublicDeficitDeltaEur)+'</strong></div>'+
      '</div>'+
      '<p class="source">Calcul comptable simple : on garde le PIB, les taux, l’inflation et les autres recettes/dépenses inchangés. Ce n’est pas encore une prévision économique complète.</p>'+
    '</section>':
    '<section class="fiscal-impact"><h3>Effet à '+horizonName+'</h3><p>Pas encore de chiffre fiable pour cette mesure. Il faut connecter les modèles indiqués plus bas avant de faire varier emploi, PIB, revenus, prix ou services publics.</p></section>';

  const hypothesisCases=hypotheses.cases.map((item,i)=>{
    const affected=(item.affected_variables||[]).map(v=>humanize(v,VARIABLE_LABELS)).join(", ")||"pas encore défini";
    return '<div class="case-card">'+
      '<div class="case-title"><strong>'+(i+1)+'. '+item.label+'</strong><span class="tag">'+humanize(item.evidence,EVIDENCE_LABELS)+'</span></div>'+
      '<p><b>Ce qui peut changer :</b> '+affected+'</p>'+
    '</div>';
  }).join("");

  const interactionsHtml=hypotheses.interactions.length
    ? hypotheses.interactions.map(x=>'<li><strong>'+x.label+'</strong> — '+x.why+'</li>').join("")
    : '<li>Aucune combinaison particulière détectée entre les mesures saisies.</li>';

  const scenarioBranchesHtml=hypotheses.scenarioBranches.length
    ? tags(hypotheses.scenarioBranches,SCENARIO_LABELS)
    : '<span class="muted">Aucun scénario alternatif obligatoire pour les mesures reconnues.</span>';

  const horizonFocus=(hypotheses.horizon?.focus||[]).map(x=>'<li>'+x+'</li>').join("");
  const missingDetailsHtml=hypotheses.missingDetails.length
    ? hypotheses.missingDetails.map(tag).join(" ")
    : '<span class="muted">Aucune information supplémentaire demandée.</span>';
  const modelList=hypotheses.models.length
    ? tags(hypotheses.models,MODEL_LABELS)
    : '<span class="muted">Aucun calcul supplémentaire à connecter.</span>';
  const exogenousHtml=tags(hypotheses.exogenousVariables,EXOGENOUS_LABELS);
  const affectedHtml=hypotheses.affectedVariables.length
    ? tags(hypotheses.affectedVariables,VARIABLE_LABELS)
    : '<span class="muted">Aucun indicateur identifié.</span>';

  const hypothesisHtml=
    '<section class="hypothesis-panel">'+
      '<h3>Ce que le simulateur prend en compte</h3>'+
      '<p class="source">Pour chaque mesure, Après distingue ce qu’il peut calculer directement, ce qu’il peut estimer avec un modèle et ce qui dépend de plusieurs scénarios possibles.</p>'+
      '<div class="case-grid">'+hypothesisCases+'</div>'+
      '<details open><summary>Ce qui compte à '+horizonName+'</summary><ul>'+horizonFocus+'</ul><p>Incertitude à cet horizon : <strong>'+humanize(hypotheses.horizon.uncertainty,UNCERTAINTY_LABELS)+'</strong></p></details>'+
      '<details><summary>Informations encore manquantes pour mieux calculer</summary><div class="tag-cloud">'+missingDetailsHtml+'</div></details>'+
      '<details><summary>Mesures qui se combinent entre elles</summary><ul>'+interactionsHtml+'</ul></details>'+
      '<details><summary>Scénarios possibles à distinguer</summary><div class="tag-cloud">'+scenarioBranchesHtml+'</div></details>'+
      '<details><summary>Calculs encore à connecter</summary><div class="tag-cloud">'+modelList+'</div></details>'+
      '<details><summary>Indicateurs qui pourraient changer</summary><div class="tag-cloud">'+affectedHtml+'</div></details>'+
      '<details><summary>Éléments extérieurs qui peuvent changer le résultat</summary><div class="tag-cloud">'+exogenousHtml+'</div></details>'+
    '</section>';

  result.innerHTML=
    dashboardHtml+
    '<details class="sim-details"><summary>Voir le détail du calcul et des hypothèses</summary><div class="grid">'+
      '<section><h3>Ce que le simulateur a compris</h3><p>'+policies.length+' mesure(s)</p><ul>'+classifications+'</ul>'+
        '<p>Niveau de calcul : <strong>'+humanize(simulation.confidence,CONFIDENCE_LABELS)+'</strong></p>'+
        '<p>Incertitude à cet horizon : <strong>'+humanize(simulation.downstreamUncertainty,UNCERTAINTY_LABELS)+'</strong></p></section>'+
      '<section><h3>Ce qu’on peut déjà calculer</h3><ul>'+direct+'</ul></section>'+
      fiscalHtml+
      '<section><h3>Ce qu’il manque pour aller plus loin</h3><div class="tag-cloud">'+missingCalculations+'</div></section>'+
      '<section><h3>À savoir sur ce résultat</h3><ul>'+notes+'</ul></section>'+
      hypothesisHtml+
    "</div></details>";
}

preset.value=presets[0].id;
preset.dispatchEvent(new Event("change"));
