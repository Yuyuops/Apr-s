export const RULES = [
  ["minimum_wage", ["smic", "salaire minimum"]],
  ["retirement_age", ["retraite à", "âge de départ"]],
  ["taxation", ["impôt", "taxe", "cotisation", "prélèvement obligatoire"]],
  ["public_spending", ["dépenses publiques", "budget"]],
  ["social_benefit", ["minima sociaux", "allocation", "aide sociale"]],
  ["healthcare", ["hôpital", "désert médical", "santé", "médicament"]],
  ["education", ["éducation", "école", "enseignement"]],
  ["justice", ["justice"]],
  ["immigration", ["immigration", "asile", "étranger"]],
  ["environment", ["écologique", "transition", "incendie", "littoral"]],
  ["transport", ["rail", "transport"]],
  ["administrative_layer", ["supprimer les régions", "suppression des régions"]],
  ["eu_exit", ["sortir de l'union européenne", "sortie de l'union européenne", "frexit"]],
  ["euro_exit", ["sortir de l'euro", "sortie de l'euro"]],
  ["nato_exit", ["sortir de l'otan", "sortie de l'otan", "quitter l'otan"]],
  ["constitutional_reform", ["assemblée constituante", "6e république", "constitution", "référendum"]],
  ["public_service", ["service public", "services publics"]],
  ["security", ["police", "sécurité", "délinquance"]],
  ["housing", ["logement"]],
  ["defence", ["défense", "armée", "militaire"]],
  ["energy", ["énergie", "renouvelable", "nucléaire"]],
];

export const CAPABILITIES = {
  minimum_wage: ["tax_benefit_rules", "labour_market", "macroeconomy"],
  retirement_age: ["pension_system", "labour_market", "public_finance"],
  taxation: ["tax_benefit_rules", "public_finance", "distribution"],
  public_spending: ["public_finance", "macroeconomy"],
  social_benefit: ["tax_benefit_rules", "take_up_model", "public_finance"],
  healthcare: ["health_system", "public_finance", "regional_access"],
  education: ["education_system", "public_finance"],
  justice: ["justice_system"],
  immigration: ["migration_system", "public_finance", "labour_market"],
  environment: ["environment_energy", "public_finance"],
  transport: ["transport_system", "environment_energy", "public_finance"],
  administrative_layer: ["administrative_layer_removal", "competence_transfer", "public_finance"],
  eu_exit: ["international_treaty_exit", "trade_regime", "public_finance", "macroeconomy"],
  euro_exit: ["monetary_regime_change", "banking_finance", "macroeconomy"],
  nato_exit: ["international_treaty_exit", "defence_posture"],
  constitutional_reform: ["constitutional_change", "institutional_graph"],
  public_service: ["public_finance", "public_service_capacity"],
  security: ["security_system", "public_finance"],
  housing: ["housing_market", "public_finance", "distribution"],
  defence: ["defence_posture", "public_finance"],
  energy: ["environment_energy", "energy_system", "public_finance"],
};

const SCENARIO = new Set(["eu_exit","euro_exit","nato_exit","constitutional_reform"]);

function extractNumber(text){
  const m=text.toLowerCase().match(/(\d[\d\s]*(?:[,.]\d+)?)\s*(%|euros?|€|milliards?|millions?)?/);
  if(!m) return {value:null, unit:null};
  return {value:Number(m[1].replaceAll(" ","").replace(",",".")), unit:m[2]||null};
}

function detectAction(text){
  const t=text.toLowerCase();
  if(["augmenter","hausser","accroître","renforcer","développer","créer"].some(x=>t.includes(x))) return "INCREASE";
  if(["réduire","baisser","diminuer","supprimer","abolir"].some(x=>t.includes(x))) return "DECREASE";
  if(["porter","fixer","établir"].some(x=>t.includes(x))) return "SET";
  return "STRUCTURAL_CHANGE";
}

function toEur(value,unit){
  if(value==null) return null;
  if(["€","euro","euros"].includes(unit)) return value;
  if(["million","millions"].includes(unit)) return value*1e6;
  if(["milliard","milliards"].includes(unit)) return value*1e9;
  return null;
}

export function compilePolicy(text){
  const lower=text.toLowerCase();
  const found=RULES.find(([,terms])=>terms.some(term=>lower.includes(term)));
  const target=found?found[0]:"unknown";
  const {value,unit}=extractNumber(text);
  return {
    text,target,value,unit,action:detectAction(text),
    evidenceClass: target==="unknown"?"unknown":SCENARIO.has(target)?"scenario_only":"modelisable",
    requiredCapabilities: CAPABILITIES[target]||[],
  };
}

function horizonUncertainty(horizonMonths){
  if(horizonMonths <= 6) return "low";
  if(horizonMonths <= 12) return "medium";
  if(horizonMonths <= 24) return "high";
  return "very_high";
}

export function simulatePolicy(policy,horizonMonths){
  if(horizonMonths<=0) throw new Error("horizonMonths must be > 0");
  const directEffects={};
  const missing=[...policy.requiredCapabilities];
  const assumptions=[];
  const scenarioNotes=[];
  const lower=policy.text.toLowerCase();
  const annual=/(par an|\/an|annuel|annuelle)/.test(lower)?toEur(policy.value,policy.unit):null;
  const sign=policy.action==="INCREASE"?1:policy.action==="DECREASE"?-1:null;

  if(policy.target==="public_spending" && annual!=null && sign!=null){
    directEffects.annual_public_spending_delta_eur=sign*annual;
    directEffects.cumulative_public_spending_delta_eur=sign*annual*horizonMonths/12;
    assumptions.push("Effet comptable calculé uniquement à partir d'un montant annuel explicitement indiqué.");
    const i=missing.indexOf("public_finance"); if(i>=0) missing.splice(i,1);
  }
  if(policy.target==="taxation" && annual!=null && sign!=null){
    directEffects.annual_public_revenue_delta_eur=sign*annual;
    directEffects.cumulative_public_revenue_delta_eur=sign*annual*horizonMonths/12;
    assumptions.push("Effet comptable calculé uniquement à partir d'un montant annuel explicitement indiqué.");
    const i=missing.indexOf("public_finance"); if(i>=0) missing.splice(i,1);
  }
  if(SCENARIO.has(policy.target)){
    scenarioNotes.push("Réforme structurelle : les effets aval nécessitent des scénarios explicites, pas un chiffre unique inventé.");
  }
  if(policy.value!=null && toEur(policy.value,policy.unit)!=null && annual==null){
    assumptions.push("Montant détecté sans périodicité annuelle explicite : aucun flux récurrent n'est supposé.");
  }
  return {
    horizonMonths,
    directEffects,
    modeledEffects:{},
    scenarioNotes,
    missingCapabilities:[...new Set(missing)],
    assumptions,
    confidence:Object.keys(directEffects).length?"high_for_accounting_effect_only":scenarioNotes.length?"scenario_only":"unknown",
    downstreamUncertainty:horizonUncertainty(horizonMonths),
  };
}
