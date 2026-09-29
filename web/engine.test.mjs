import test from "node:test";
import assert from "node:assert/strict";
import {compilePolicy,simulatePolicy} from "./engine.js";

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
