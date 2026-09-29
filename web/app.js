import {compilePolicy,simulatePolicy} from "./engine.js";

const measure=document.querySelector("#measure");
const preset=document.querySelector("#preset");
const horizon=document.querySelector("#horizon");
const horizonLabel=document.querySelector("#horizonLabel");
const result=document.querySelector("#result");
const sourceBox=document.querySelector("#sourceBox");

const presets=await fetch("./demo-policies.json").then(r=>r.json());
for(const p of presets){
  const o=document.createElement("option");
  o.value=p.id;
  o.textContent=p.label;
  preset.appendChild(o);
}

preset.addEventListener("change",()=>{
  const p=presets.find(x=>x.id===preset.value);
  if(!p) return;
  measure.value=p.text;
  if(p.source){
    sourceBox.innerHTML='Source déclarée : <a href="'+p.source+'" target="_blank" rel="noreferrer">'+p.source+'</a> · statut : '+p.status;
  } else {
    sourceBox.textContent="Mesure synthétique de démonstration.";
  }
  render();
});

measure.addEventListener("input",()=>{
  preset.value="";
  sourceBox.textContent="Entrée utilisateur non attribuée.";
  render();
});
horizon.addEventListener("input",render);

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
  const p=compilePolicy(measure.value);
  const s=simulatePolicy(p,months);
  const direct=Object.entries(s.directEffects).map(([k,v])=>"<li><code>"+k+"</code> : <strong>"+eur(v)+"</strong></li>").join("")||"<li>Aucun effet comptable direct calculable avec les informations fournies.</li>";
  const caps=s.missingCapabilities.map(tag).join(" ")||"Aucune capacité manquante pour l'effet direct affiché.";
  const notes=[...s.scenarioNotes,...s.assumptions].map(x=>"<li>"+x+"</li>").join("")||"<li>Aucune hypothèse supplémentaire.</li>";
  result.innerHTML=
    '<div class="grid">'+
      '<section><h3>Classification</h3><p><strong>'+p.target+'</strong></p><p>Action : '+p.action+'</p><p>Confiance : '+s.confidence+'</p><p>Incertitude aval à cet horizon : <strong>'+s.downstreamUncertainty+'</strong></p></section>'+
      '<section><h3>Effets directs</h3><ul>'+direct+'</ul></section>'+
      '<section><h3>Capacités encore nécessaires</h3><div>'+caps+'</div></section>'+
      '<section><h3>Hypothèses / scénarios</h3><ul>'+notes+'</ul></section>'+
    "</div>";
}

preset.value=presets[0].id;
preset.dispatchEvent(new Event("change"));
