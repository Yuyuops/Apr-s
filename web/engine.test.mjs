import test from "node:test";
import assert from "node:assert/strict";
import {applyFiscalBaseline,compilePolicy,simulatePolicy,simulateProgram} from "./engine.js";

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
