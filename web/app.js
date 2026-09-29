import {applyFiscalBaseline,compilePolicy,simulateProgram} from "./engine.js";
import {hypothesisSummary} from "./hypotheses.js";

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
  '<div class="baseline-head"><div><span class="eyebrow">BASELINE OFFICIELLE</span><h2>France '+baseline.period+'</h2></div>'+
  '<div class="baseline-source">Insee · récupéré le '+baseline.retrieved_at+'</div></div>'+
  '<div class="baseline-grid">'+
    '<div><span>PIB</span><strong>'+formatBn(baseline.gdp_eur)+'</strong></div>'+
    '<div><span>Dépenses publiques</span><strong>'+formatBn(baseline.public_expenditure_eur)+'</strong></div>'+
    '<div><span>Déficit public</span><strong>'+formatBn(baseline.public_deficit_eur)+' · '+baseline.public_deficit_pct_gdp+' % PIB</strong></div>'+
    '<div><span>Dette publique</span><strong>'+baseline.public_debt_pct_gdp+' % PIB</strong></div>'+
  '</div>';

preset.addEventListener("change",()=>{
  const p=presets.find(x=>x.id===preset.value);
  if(!p) return;
  measure.value=p.text;
  if(p.source){
    sourceBox.innerHTML='Source déclarée : <a href="'+p.source+'" target="_blank" rel="noreferrer">'+p.source+'</a> · statut : '+p.status;
  } else {
    sourceBox.textContent="Mesure(s) synthétique(s) de démonstration.";
  }
  render();
});

measure.addEventListener("input",()=>{
  preset.value="";
  sourceBox.textContent="Entrée utilisateur non attribuée.";
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
function horizonText(months){
  return months===1?"1 mois":months===6?"6 mois":months===12?"1 an":months===24?"2 ans":months===60?"5 ans":months+" mois";
}
function directLabel(key){
  return ({
    annual_public_spending_delta_eur:"Dépenses publiques — rythme annuel",
    cumulative_public_spending_delta_eur:"Dépenses publiques — cumul à l'horizon",
    annual_public_revenue_delta_eur:"Recettes publiques — rythme annuel",
    cumulative_public_revenue_delta_eur:"Recettes publiques — cumul à l'horizon"
  })[key]||key;
}

function render(){
  const months=Number(horizon.value);
  const horizonName=horizonText(months);
  horizonLabel.textContent=horizonName;

  const texts=measure.value.split(/\n+/).map(x=>x.trim()).filter(Boolean);
  const policies=texts.map(compilePolicy);
  const s=simulateProgram(policies,months);
  const fiscal=applyFiscalBaseline(s,baseline);
  const h=hypothesisSummary(policies,hypothesisRegistry,months);

  const classifications=policies.map((p,i)=>
    "<li><strong>"+(i+1)+". "+p.target+"</strong> · "+p.action+"</li>"
  ).join("")||"<li>Aucune mesure saisie.</li>";

  const direct=Object.entries(s.directEffects)
    .map(([k,v])=>"<li><span>"+directLabel(k)+"</span> : <strong>"+eur(v)+"</strong></li>")
    .join("")||"<li>Aucun effet comptable direct calculable avec les informations fournies.</li>";

  const caps=s.missingCapabilities.map(tag).join(" ")||"Aucune capacité manquante pour l'effet direct affiché.";
  const notes=[...s.scenarioNotes,...s.assumptions]
    .map(x=>"<li>"+x+"</li>").join("")||"<li>Aucune hypothèse supplémentaire.</li>";

  const fiscalHtml=fiscal?
    '<section class="fiscal-impact"><h3>Impact direct à '+horizonName+'</h3>'+
      '<div class="impact-primary"><span>Variation cumulée du déficit</span><strong>'+eur(fiscal.cumulativePublicDeficitDeltaEur)+'</strong></div>'+
      '<div class="impact-grid">'+
        '<div><span>Dépenses cumulées</span><strong>'+eur(fiscal.cumulativePublicSpendingDeltaEur)+'</strong></div>'+
        '<div><span>Recettes cumulées</span><strong>'+eur(fiscal.cumulativePublicRevenueDeltaEur)+'</strong></div>'+
        '<div><span>Impact dette vs baseline</span><strong>'+((fiscal.cumulativeDebtImpactPctGdp>=0?"+":"")+fiscal.cumulativeDebtImpactPctGdp.toFixed(3))+' pt PIB</strong></div>'+
        '<div><span>Variation annuelle du déficit</span><strong>'+eur(fiscal.annualPublicDeficitDeltaEur)+'</strong></div>'+
      '</div>'+
      '<p class="source">'+fiscal.assumption+'</p>'+
    '</section>':
    '<section class="fiscal-impact"><h3>Impact direct à '+horizonName+'</h3><p>Aucun flux budgétaire temporel calculable pour ces mesures. Le curseur ne peut donc modifier que l’incertitude tant qu’un modèle causal validé n’est pas branché.</p></section>';

  const hypothesisCases=h.cases.map((item,i)=>
    '<div class="case-card">'+
      '<div class="case-title"><strong>'+(i+1)+'. '+item.label+'</strong><span class="tag">'+item.evidence+'</span></div>'+
      '<div class="case-meta">'+item.layer+'</div>'+
      '<p><b>Modèles attendus :</b> '+((item.models||[]).join(", ")||"aucun")+'</p>'+
      '<p><b>Variables touchées :</b> '+((item.affected_variables||[]).join(", ")||"non définies")+'</p>'+
    '</div>'
  ).join("");

  const interactionsHtml=h.interactions.length
    ? h.interactions.map(x=>'<li><strong>'+x.label+'</strong> — '+x.why+'</li>').join("")
    : '<li>Aucune interaction prédéfinie détectée sur ce paquet.</li>';

  const scenarioBranchesHtml=h.scenarioBranches.length
    ? h.scenarioBranches.map(tag).join(" ")
    : '<span class="muted">Aucune branche de scénario explicite requise pour les cas reconnus.</span>';

  const horizonFocus=(h.horizon?.focus||[]).map(x=>'<li>'+x+'</li>').join("");
  const missingDetailsHtml=h.missingDetails.map(tag).join(" ")||'<span class="muted">Aucune précision supplémentaire enregistrée.</span>';
  const modelList=h.models.map(tag).join(" ")||'<span class="muted">Aucun modèle déclaré.</span>';
  const exogenousHtml=h.exogenousVariables.map(tag).join(" ");
  const affectedHtml=h.affectedVariables.map(tag).join(" ")||'<span class="muted">Aucune variable déclarée.</span>';

  const hypothesisHtml=
    '<section class="hypothesis-panel">'+
      '<h3>Hypothèses et cas pris en compte</h3>'+
      '<p class="source">Registre méthodologique : '+hypothesisRegistry.cases.length+' cas, '+hypothesisRegistry.interactions.length+' interactions, '+hypothesisRegistry.exogenous_variables.length+' variables exogènes.</p>'+
      '<div class="case-grid">'+hypothesisCases+'</div>'+
      '<details open><summary>À cet horizon : '+horizonName+'</summary><ul>'+horizonFocus+'</ul><p>Classe d’incertitude méthodologique : <strong>'+h.horizon.uncertainty+'</strong></p></details>'+
      '<details><summary>Informations à préciser avant chiffrage complet</summary><div class="tag-cloud">'+missingDetailsHtml+'</div></details>'+
      '<details><summary>Interactions détectées</summary><ul>'+interactionsHtml+'</ul></details>'+
      '<details><summary>Branches de scénario à résoudre</summary><div class="tag-cloud">'+scenarioBranchesHtml+'</div></details>'+
      '<details><summary>Modèles à brancher</summary><div class="tag-cloud">'+modelList+'</div></details>'+
      '<details><summary>Variables potentiellement affectées</summary><div class="tag-cloud">'+affectedHtml+'</div></details>'+
      '<details><summary>Variables exogènes à suivre</summary><div class="tag-cloud">'+exogenousHtml+'</div></details>'+
    '</section>';

  result.innerHTML=
    '<div class="grid">'+
      '<section><h3>Classification</h3><p>'+policies.length+' mesure(s)</p><ul>'+classifications+'</ul><p>Confiance : '+s.confidence+'</p><p>Incertitude aval : <strong>'+s.downstreamUncertainty+'</strong></p></section>'+
      '<section><h3>Effets directs</h3><ul>'+direct+'</ul></section>'+
      fiscalHtml+
      '<section><h3>Capacités encore nécessaires</h3><div>'+caps+'</div></section>'+
      '<section><h3>Hypothèses / scénarios</h3><ul>'+notes+'</ul></section>'+ 
      hypothesisHtml+
    "</div>";
}

preset.value=presets[0].id;
preset.dispatchEvent(new Event("change"));
