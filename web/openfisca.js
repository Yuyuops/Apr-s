export const OPENFISCA_FRANCE_API = "https://api.fr.openfisca.org/latest";
export const SMIC_HOURLY_PARAMETER = "marche_travail.salaire_minimum.smic.smic_b_horaire";

export function latestParameterValue(parameter){
  const entries=Object.entries(parameter?.values||{})
    .filter(([,value])=>typeof value==="number")
    .sort(([a],[b])=>a.localeCompare(b));
  if(!entries.length) return null;
  const [date,value]=entries.at(-1);
  return {date,value};
}

export async function fetchSmicHourly(fetchImpl=fetch){
  const url=OPENFISCA_FRANCE_API+"/parameter/"+SMIC_HOURLY_PARAMETER;
  const response=await fetchImpl(url,{headers:{"Accept":"application/json"}});
  if(!response.ok) throw new Error("OpenFisca HTTP "+response.status);
  const parameter=await response.json();
  const latest=latestParameterValue(parameter);
  if(!latest) throw new Error("OpenFisca parameter has no numeric value");
  return {
    id:parameter.id,
    label:parameter.description||"SMIC horaire brut",
    value:latest.value,
    effectiveDate:latest.date,
    sourceUrl:url,
    packageVersion:response.headers.get("country-package-version")||null
  };
}

export function buildDirectParameterChanges(policies,referenceData){
  const changes=[];
  const smic=referenceData?.smicHourly;

  for(const policy of policies){
    const text=policy.text.toLowerCase();
    if(policy.target==="minimum_wage" && policy.value!=null && smic){
      const isHourly=/(horaire|par heure|\/h)/.test(text);
      const isEuro=policy.unit==="€" || policy.unit==="euro" || policy.unit==="euros";
      if(isHourly && isEuro){
        const target=Number(policy.value);
        changes.push({
          id:"smic_hourly",
          label:"SMIC horaire brut",
          baseline:smic.value,
          projected:target,
          unit:"€/h",
          delta:target-smic.value,
          deltaPct:100*(target-smic.value)/smic.value,
          effectiveDate:smic.effectiveDate,
          sourceUrl:smic.sourceUrl,
          sourceLabel:"OpenFisca France",
          confidence:"Calcul direct"
        });
      }
    }
  }

  return changes;
}
