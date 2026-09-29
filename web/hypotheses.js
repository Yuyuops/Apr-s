export function activeHorizonProfile(registry,horizonMonths){
  const exact=registry.horizon_method.find(x=>x.months===horizonMonths);
  if(exact) return exact;
  const sorted=[...registry.horizon_method].sort((a,b)=>a.months-b.months);
  let candidate=sorted[0];
  for(const item of sorted){
    if(item.months<=horizonMonths) candidate=item;
  }
  return candidate;
}

export function applicableCases(policies,registry){
  return policies.map((policy,index)=>{
    const match=registry.cases.find(c=>c.targets.includes(policy.target))
      || registry.cases.find(c=>c.targets.includes("unknown"));
    return {policyIndex:index,policyTarget:policy.target,...match};
  });
}

export function detectedInteractions(policies,registry){
  const targets=new Set(policies.map(p=>p.target));
  return registry.interactions.filter(interaction=>
    interaction.requires_any.some(group=>group.every(target=>targets.has(target)))
  );
}

export function hypothesisSummary(policies,registry,horizonMonths){
  const cases=applicableCases(policies,registry);
  const interactions=detectedInteractions(policies,registry);
  const missingDetails=[...new Set(cases.flatMap(c=>c.required_details||[]))];
  const affectedVariables=[...new Set(cases.flatMap(c=>c.affected_variables||[]))];
  const models=[...new Set(cases.flatMap(c=>c.models||[]))];
  const scenarioBranches=[...new Set(cases.flatMap(c=>c.scenario_branches||[]))];

  return {
    horizon:activeHorizonProfile(registry,horizonMonths),
    cases,
    interactions,
    missingDetails,
    affectedVariables,
    models,
    scenarioBranches,
    exogenousVariables:registry.exogenous_variables
  };
}
