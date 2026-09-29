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
