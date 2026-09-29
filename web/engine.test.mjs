import test from "node:test";
import assert from "node:assert/strict";
import {applyFiscalBaseline,compilePolicy,simulatePolicy,simulateProgram} from "./engine.js";
import {hypothesisSummary} from "./hypotheses.js";

test("annual spending scales with horizon",()=>{
  const p=compilePolicy("Augmenter les dépenses publiques de 12 milliards d'euros par an");
  const r=simulatePolicy(p,6);
  assert.equal(r.directEffects.cumulative_public_spending_delta_eur,6_000_000_000);
});

test("tax cut lowers revenue",()=>{
  const p=compilePolicy("Réduire les impôts de 2 milliards d'euros par an");
  const r=simulatePolicy(p,12);
  assert.equal(r.directEffects.annual_public_revenue_delta_eur,-2_000_000_000);
});

test("structural reform does not fabricate causal number",()=>{
  const p=compilePolicy("Sortir de l'Union européenne");
  const r=simulatePolicy(p,60);
  assert.deepEqual(r.directEffects,{});
  assert.equal(r.confidence,"scenario_only");
});

test("downstream uncertainty grows with the horizon",()=>{
  const p=compilePolicy("Augmenter les dépenses publiques de 1 milliard d'euros par an");
  assert.equal(simulatePolicy(p,1).downstreamUncertainty,"low");
  assert.equal(simulatePolicy(p,12).downstreamUncertainty,"medium");
  assert.equal(simulatePolicy(p,24).downstreamUncertainty,"high");
  assert.equal(simulatePolicy(p,60).downstreamUncertainty,"very_high");
});


test("programme aggregates direct fiscal effects",()=>{
  const policies=[
    compilePolicy("Augmenter les dépenses publiques de 12 milliards d'euros par an"),
    compilePolicy("Réduire les impôts de 2 milliards d'euros par an")
  ];
  const r=simulateProgram(policies,12);
  assert.equal(r.directEffects.annual_public_spending_delta_eur,12_000_000_000);
  assert.equal(r.directEffects.annual_public_revenue_delta_eur,-2_000_000_000);
  assert.ok(r.missingCapabilities.includes("policy_interaction_model"));
});

test("official baseline produces ceteris-paribus deficit snapshot",()=>{
  const policies=[compilePolicy("Augmenter les dépenses publiques de 12 milliards d'euros par an")];
  const r=simulateProgram(policies,12);
  const baseline={id:"france_2025_insee",period:"2025",gdp_eur:2_991_100_000_000,public_deficit_eur:152_500_000_000};
  const s=applyFiscalBaseline(r,baseline);
  assert.equal(s.annualPublicDeficitDeltaEur,12_000_000_000);
  assert.equal(s.annualPublicDeficitAfterDirectEffectEur,164_500_000_000);
});


test("testable UI supports one measure per line without escaped markup", async()=>{
  const fs = await import("node:fs/promises");
  const html = await fs.readFile(new URL("./index.html", import.meta.url), "utf8");
  assert.match(html, /une mesure par ligne/i);
  assert.equal(html.includes("\\n\\n"), false);
});


test("fiscal baseline cumulative impact changes with slider horizon",()=>{
  const policy=compilePolicy("Augmenter les dépenses publiques de 12 milliards d'euros par an");
  const baseline={id:"france_2025_insee",period:"2025",gdp_eur:2_991_100_000_000,public_deficit_eur:152_500_000_000};

  const six=applyFiscalBaseline(simulateProgram([policy],6),baseline);
  const sixty=applyFiscalBaseline(simulateProgram([policy],60),baseline);

  assert.equal(six.cumulativePublicDeficitDeltaEur,6_000_000_000);
  assert.equal(sixty.cumulativePublicDeficitDeltaEur,60_000_000_000);
  assert.ok(sixty.cumulativeDebtImpactPctGdp>six.cumulativeDebtImpactPctGdp);
});


test("hypothesis registry covers the identified structural and sector cases", async()=>{
  const fs=await import("node:fs/promises");
  const registry=JSON.parse(await fs.readFile(new URL("./hypotheses_registry.json",import.meta.url),"utf8"));
  const ids=new Set(registry.cases.map(x=>x.id));
  for(const expected of [
    "minimum_wage","retirement_age","taxation","public_spending","social_benefit",
    "healthcare","education","justice","security","immigration","housing","environment",
    "energy","transport","administrative_layer","administrative_reorganisation",
    "eu_exit","euro_exit","nato_exit","schengen_or_eu_rule","constitutional_reform",
    "privatisation_nationalisation","foreign_policy","defence","public_service",
    "digital_policy","objective_only"
  ]){
    assert.ok(ids.has(expected), "missing case "+expected);
  }
});

test("combined EU and euro changes trigger an explicit interaction", async()=>{
  const fs=await import("node:fs/promises");
  const registry=JSON.parse(await fs.readFile(new URL("./hypotheses_registry.json",import.meta.url),"utf8"));
  const policies=[
    compilePolicy("Sortir de l'Union européenne"),
    compilePolicy("Sortir de l'euro")
  ];
  const summary=hypothesisSummary(policies,registry,60);
  assert.ok(summary.interactions.some(x=>x.id==="eu_euro_combo"));
  assert.ok(summary.scenarioBranches.includes("relation_future_non_precisee"));
  assert.ok(summary.scenarioBranches.includes("nouvelle_monnaie_non_precisee"));
});

test("administrative layer removal requires competence transfer details", async()=>{
  const fs=await import("node:fs/promises");
  const registry=JSON.parse(await fs.readFile(new URL("./hypotheses_registry.json",import.meta.url),"utf8"));
  const summary=hypothesisSummary([compilePolicy("Supprimer les régions")],registry,24);
  assert.ok(summary.missingDetails.includes("compétences transférées"));
  assert.ok(summary.models.includes("competence_transfer"));
});

test("all five modelling horizons are encoded", async()=>{
  const fs=await import("node:fs/promises");
  const registry=JSON.parse(await fs.readFile(new URL("./hypotheses_registry.json",import.meta.url),"utf8"));
  assert.deepEqual(registry.horizon_method.map(x=>x.months),[1,6,12,24,60]);
});


test("plain-language UI hides core technical codes", async()=>{
  const fs=await import("node:fs/promises");
  const app=await fs.readFile(new URL("./app.js",import.meta.url),"utf8");
  for(const forbidden of [
    "Capacités encore nécessaires",
    "Incertitude aval",
    "Modèles attendus",
    "Variables exogènes",
    "Classification"
  ]){
    assert.equal(app.includes(forbidden),false,"technical wording still visible: "+forbidden);
  }
});

test("technical engine values have human labels", async()=>{
  const labels=await import("./labels.js");
  assert.equal(labels.TARGET_LABELS.public_spending,"Dépenses publiques");
  assert.equal(labels.CONFIDENCE_LABELS.high_for_accounting_effects_only,"Calculs directs fiables");
  assert.equal(labels.UNCERTAINTY_LABELS.very_high,"Très élevée");
  assert.equal(labels.MODEL_LABELS.macroeconomy,"Économie globale");
  assert.equal(labels.MODEL_LABELS.policy_interaction_model,"Effets combinés entre les mesures");
  assert.equal(labels.EXOGENOUS_LABELS.taux_BCE,"Taux d'intérêt de la BCE");
});


test("every engine target and capability has a reader-friendly label", async()=>{
  const labels=await import("./labels.js");
  const engine=await import("./engine.js");
  for(const [target,capabilities] of Object.entries(engine.CAPABILITIES)){
    assert.ok(labels.TARGET_LABELS[target],"missing target label: "+target);
    for(const capability of capabilities){
      assert.ok(labels.MODEL_LABELS[capability],"missing capability label: "+capability);
    }
  }
});

test("every registry evidence and external factor has a reader-friendly label", async()=>{
  const fs=await import("node:fs/promises");
  const labels=await import("./labels.js");
  const registry=JSON.parse(await fs.readFile(new URL("./hypotheses_registry.json",import.meta.url),"utf8"));
  for(const item of registry.cases){
    assert.ok(labels.EVIDENCE_LABELS[item.evidence],"missing evidence label: "+item.evidence);
  }
  for(const factor of registry.exogenous_variables){
    assert.ok(labels.EXOGENOUS_LABELS[factor],"missing external-factor label: "+factor);
  }
});


test("SimCity dashboard exposes 14 public indicators", async()=>{
  const dashboard=await import("./dashboard.js");
  const fs=await import("node:fs/promises");
  const registry=JSON.parse(await fs.readFile(new URL("./hypotheses_registry.json",import.meta.url),"utf8"));
  const baseline=JSON.parse(await fs.readFile(new URL("./france_2025.json",import.meta.url),"utf8"));
  const policies=[
    compilePolicy("Augmenter les dépenses publiques de 12 milliards d'euros par an"),
    compilePolicy("Réduire les impôts de 2 milliards d'euros par an")
  ];
  const simulation=simulateProgram(policies,12);
  const fiscal=applyFiscalBaseline(simulation,baseline);
  const {hypothesisSummary}=await import("./hypotheses.js");
  const hypotheses=hypothesisSummary(policies,registry,12);
  const state=dashboard.buildDashboardState({policies,simulation,fiscal,baseline,hypotheses});

  assert.equal(state.indicators.length,14);
  assert.equal(state.indicators.find(x=>x.id==="spending").status,"calculated");
  assert.equal(state.indicators.find(x=>x.id==="revenue").status,"calculated");
  assert.equal(state.indicators.find(x=>x.id==="deficit").status,"calculated");
  assert.equal(state.indicators.find(x=>x.id==="debt").status,"calculated");
  assert.ok(state.summary.calculated>=4);
});

test("structural policy activates institution scenario card", async()=>{
  const dashboard=await import("./dashboard.js");
  const fs=await import("node:fs/promises");
  const registry=JSON.parse(await fs.readFile(new URL("./hypotheses_registry.json",import.meta.url),"utf8"));
  const baseline=JSON.parse(await fs.readFile(new URL("./france_2025.json",import.meta.url),"utf8"));
  const policies=[compilePolicy("Sortir de l'Union européenne")];
  const simulation=simulateProgram(policies,60);
  const {hypothesisSummary}=await import("./hypotheses.js");
  const hypotheses=hypothesisSummary(policies,registry,60);
  const state=dashboard.buildDashboardState({policies,simulation,fiscal:null,baseline,hypotheses});

  assert.equal(state.indicators.find(x=>x.id==="institutions").status,"scenario");
});


test("measure typology covers the 16 product categories", async()=>{
  const {MEASURE_TYPES,detectMeasureType}=await import("./measure-types.js");
  assert.equal(Object.keys(MEASURE_TYPES).length,16);

  assert.equal(detectMeasureType(compilePolicy("Porter le SMIC à 2000 euros")),"parametric");
  assert.equal(detectMeasureType(compilePolicy("Augmenter les dépenses publiques de 12 milliards d'euros par an")),"budgetary");
  assert.equal(detectMeasureType(compilePolicy("Créer une nouvelle taxe")),"fiscal_social");
  assert.equal(detectMeasureType(compilePolicy("Supprimer les régions")),"administrative");
  assert.equal(detectMeasureType(compilePolicy("Sortir de l'Union européenne")),"treaty");
  assert.equal(detectMeasureType(compilePolicy("Sortir de l'euro")),"monetary");
});

test("UX exposes five quick time horizons and a reset control", async()=>{
  const fs=await import("node:fs/promises");
  const html=await fs.readFile(new URL("./index.html",import.meta.url),"utf8");
  for(const months of ["1","6","12","24","60"]){
    assert.match(html,new RegExp('data-months="'+months+'"'));
  }
  assert.match(html,/id="resetButton"/);
  assert.match(html,/Le tableau de bord se met à jour automatiquement/);
});

test("calculated dashboard cards include time trajectories", async()=>{
  const dashboard=await import("./dashboard.js");
  const fs=await import("node:fs/promises");
  const registry=JSON.parse(await fs.readFile(new URL("./hypotheses_registry.json",import.meta.url),"utf8"));
  const baseline=JSON.parse(await fs.readFile(new URL("./france_2025.json",import.meta.url),"utf8"));
  const policies=[compilePolicy("Augmenter les dépenses publiques de 12 milliards d'euros par an")];
  const simulation=simulateProgram(policies,60);
  const fiscal=applyFiscalBaseline(simulation,baseline);
  const hypotheses=hypothesisSummary(policies,registry,60);
  const state=dashboard.buildDashboardState({policies,simulation,fiscal,baseline,hypotheses});

  const spending=state.indicators.find(x=>x.id==="spending");
  const debt=state.indicators.find(x=>x.id==="debt");
  assert.equal(spending.trend.length,7);
  assert.equal(debt.trend.length,7);
  assert.notEqual(spending.trend[0],spending.trend.at(-1));
});


test("OpenFisca adapter selects the latest dated parameter value", async()=>{
  const {latestParameterValue}=await import("./openfisca.js");
  const latest=latestParameterValue({values:{
    "2024-01-01":11.65,
    "2026-01-01":12.02,
    "2026-06-01":12.31
  }});
  assert.deepEqual(latest,{date:"2026-06-01",value:12.31});
});

test("hourly SMIC proposal becomes a direct parameter change", async()=>{
  const {buildDirectParameterChanges}=await import("./openfisca.js");
  const policy=compilePolicy("Porter le SMIC horaire brut à 13 euros");
  const changes=buildDirectParameterChanges([policy],{
    smicHourly:{value:12.31,effectiveDate:"2026-06-01",sourceUrl:"https://example.invalid"}
  });
  assert.equal(changes.length,1);
  assert.equal(changes[0].baseline,12.31);
  assert.equal(changes[0].projected,13);
  assert.ok(changes[0].deltaPct>5);
});

test("non-hourly SMIC proposal is not silently compared to hourly baseline", async()=>{
  const {buildDirectParameterChanges}=await import("./openfisca.js");
  const policy=compilePolicy("Porter le SMIC à 2000 euros brut");
  const changes=buildDirectParameterChanges([policy],{
    smicHourly:{value:12.31,effectiveDate:"2026-06-01",sourceUrl:"https://example.invalid"}
  });
  assert.equal(changes.length,0);
});


test("explicit public staffing becomes a quantified dashboard effect", async()=>{
  const {extractDirectOperationalEffects}=await import("./direct-operational.js");
  const {buildDashboardState}=await import("./dashboard.js");
  const fs=await import("node:fs/promises");
  const registry=JSON.parse(await fs.readFile(new URL("./hypotheses_registry.json",import.meta.url),"utf8"));
  const baseline=JSON.parse(await fs.readFile(new URL("./france_2025.json",import.meta.url),"utf8"));

  const policies=[compilePolicy("Recruter 10 000 policiers")];
  const operationalEffects=extractDirectOperationalEffects(policies);
  assert.equal(operationalEffects[0].value,10000);
  assert.equal(operationalEffects[0].indicator,"security");

  const simulation=simulateProgram(policies,12);
  const hypotheses=hypothesisSummary(policies,registry,12);
  const state=buildDashboardState({policies,simulation,fiscal:null,baseline,hypotheses,operationalEffects});
  const security=state.indicators.find(x=>x.id==="security");
  assert.equal(security.status,"calculated");
  assert.match(security.delta,/10.?000/);
});

test("explicit infrastructure and energy capacity are quantified without causal guesses", async()=>{
  const {extractDirectOperationalEffects}=await import("./direct-operational.js");
  const policies=[
    compilePolicy("Construire 20 hôpitaux"),
    compilePolicy("Construire 300 km de rail"),
    compilePolicy("Ajouter 5 GW de solaire")
  ];
  const effects=extractDirectOperationalEffects(policies);
  assert.ok(effects.some(x=>x.indicator==="health" && x.value===20));
  assert.ok(effects.some(x=>x.indicator==="mobility" && x.value===300 && x.unit==="km"));
  assert.ok(effects.some(x=>x.indicator==="energy" && x.value===5 && x.unit==="GW"));
});

test("recruitment and construction verbs are treated as increases",()=>{
  assert.equal(compilePolicy("Recruter 1000 enseignants").action,"INCREASE");
  assert.equal(compilePolicy("Construire 10 prisons").action,"INCREASE");
  assert.equal(compilePolicy("Fermer 5 hôpitaux").action,"DECREASE");
});
