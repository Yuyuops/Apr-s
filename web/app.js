import {applyFiscalBaseline,compilePolicy,simulateProgram} from "./engine.js";
import {hypothesisSummary} from "./hypotheses.js";
import {buildDashboardState,groupDashboardIndicators} from "./dashboard.js";
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

const [presets,baseline,hypothesisRegistry]=await Promise.all([
  fetch("./demo-policies.json").then(r=>r.json()),
  fetch("./france_2025.json").then(r=>r.json()),
  fetch("./hypotheses_registry.json").then(r=>r.json())
]);

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
  const policies=texts.map(compilePolicy);
  const simulation=simulateProgram(policies,months);
  const fiscal=applyFiscalBaseline(simulation,baseline);
  const hypotheses=hypothesisSummary(policies,hypothesisRegistry,months);
  const dashboard=buildDashboardState({policies,simulation,fiscal,baseline,hypotheses});
  const dashboardGroups=groupDashboardIndicators(dashboard.indicators);

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

      return '<article class="sim-card sim-'+item.status+'">'+
        '<div class="sim-card-head"><span>'+item.label+'</span><small>'+item.confidence+'</small></div>'+
        values+
        delta+
        '<p>'+item.detail+'</p>'+
      '</article>';
    }).join("");

    return '<section class="sim-group"><h3>'+group+'</h3><div class="sim-cards">'+cards+'</div></section>';
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
      '<p class="sim-intro">Comme dans SimCity : le programme modifie l’état de la France. Les cartes chiffrées bougent avec le temps ; les cartes grisées indiquent les effets identifiés mais pas encore assez modélisés pour donner un chiffre fiable.</p>'+
      dashboardGroupsHtml+
    '</section>';

  const classifications=policies.map((p,i)=>
    "<li><strong>"+(i+1)+". "+humanize(p.target,TARGET_LABELS)+"</strong> · "+humanize(p.action,ACTION_LABELS)+"</li>"
  ).join("")||"<li>Aucune mesure saisie.</li>";

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
