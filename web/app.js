import {applyFiscalBaseline,compilePolicy,simulateProgram} from "./engine.js";

const measure=document.querySelector("#measure");
const preset=document.querySelector("#preset");
const horizon=document.querySelector("#horizon");
const horizonLabel=document.querySelector("#horizonLabel");
const result=document.querySelector("#result");
const sourceBox=document.querySelector("#sourceBox");
const baselineBox=document.querySelector("#baseline");

const [presets,baseline]=await Promise.all([
  fetch("./demo-policies.json").then(r=>r.json()),
  fetch("./france_2025.json").then(r=>r.json())
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

function render(){
  const months=Number(horizon.value);
  horizonLabel.textContent=months===1?"1 mois":months===6?"6 mois":months===12?"1 an":months===24?"2 ans":months===60?"5 ans":months+" mois";

  const texts=measure.value.split(/\n+/).map(x=>x.trim()).filter(Boolean);
  const policies=texts.map(compilePolicy);
  const s=simulateProgram(policies,months);
  const fiscal=applyFiscalBaseline(s,baseline);

  const classifications=policies.map((p,i)=>
    "<li><strong>"+(i+1)+". "+p.target+"</strong> · "+p.action+"</li>"
  ).join("")||"<li>Aucune mesure saisie.</li>";

  const direct=Object.entries(s.directEffects)
    .map(([k,v])=>"<li><code>"+k+"</code> : <strong>"+eur(v)+"</strong></li>")
    .join("")||"<li>Aucun effet comptable direct calculable avec les informations fournies.</li>";

  const caps=s.missingCapabilities.map(tag).join(" ")||"Aucune capacité manquante pour l'effet direct affiché.";
  const notes=[...s.scenarioNotes,...s.assumptions]
    .map(x=>"<li>"+x+"</li>").join("")||"<li>Aucune hypothèse supplémentaire.</li>";

  const fiscalHtml=fiscal?
    '<section><h3>Impact budgétaire direct vs baseline 2025</h3>'+
      '<p>Déficit 2025 : <strong>'+formatBn(fiscal.baselinePublicDeficitEur)+'</strong></p>'+
      '<p>Variation annuelle directe : <strong>'+eur(fiscal.annualPublicDeficitDeltaEur)+'</strong></p>'+
      '<p>Déficit après effet direct : <strong>'+formatBn(fiscal.annualPublicDeficitAfterDirectEffectEur)+'</strong> · <strong>'+fiscal.annualPublicDeficitAfterDirectEffectPctGdp.toFixed(2)+' % du PIB</strong></p>'+
      '<p class="source">'+fiscal.assumption+'</p>'+
    '</section>':
    '<section><h3>Impact budgétaire direct vs baseline 2025</h3><p>Non calculable pour les mesures saisies.</p></section>';

  result.innerHTML=
    '<div class="grid">'+
      '<section><h3>Classification</h3><p>'+policies.length+' mesure(s)</p><ul>'+classifications+'</ul><p>Confiance : '+s.confidence+'</p><p>Incertitude aval : <strong>'+s.downstreamUncertainty+'</strong></p></section>'+
      '<section><h3>Effets directs</h3><ul>'+direct+'</ul></section>'+
      fiscalHtml+
      '<section><h3>Capacités encore nécessaires</h3><div>'+caps+'</div></section>'+
      '<section><h3>Hypothèses / scénarios</h3><ul>'+notes+'</ul></section>'+
    "</div>";
}

preset.value=presets[0].id;
preset.dispatchEvent(new Event("change"));
