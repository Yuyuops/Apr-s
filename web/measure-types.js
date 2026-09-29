export const MEASURE_TYPES = {
  parametric: {
    label: "Changer un niveau",
    examples: "SMIC, TVA, impôt, âge de départ",
    effect: "Modifie directement une valeur ou un barème."
  },
  budgetary: {
    label: "Changer un budget",
    examples: "+X Md€ pour la défense ou la santé",
    effect: "Ajoute ou retire un flux de dépenses ou de recettes."
  },
  fiscal_social: {
    label: "Changer impôts ou aides",
    examples: "Nouvelle taxe, allocation, exonération",
    effect: "Modifie les règles qui déterminent ce que paient ou reçoivent les ménages et entreprises."
  },
  institutional: {
    label: "Changer les institutions",
    examples: "RIC, nouvelle République",
    effect: "Modifie l'organisation et les pouvoirs des institutions."
  },
  administrative: {
    label: "Réorganiser l'administration",
    examples: "Supprimer une région, fusionner des organismes",
    effect: "Déplace missions, personnels, budgets, actifs et responsabilités."
  },
  european: {
    label: "Changer la relation à l'UE",
    examples: "Modifier ou rejeter une règle européenne",
    effect: "Modifie les règles et contraintes entre la France et l'Union européenne."
  },
  treaty: {
    label: "Changer un traité",
    examples: "UE, OTAN, Schengen",
    effect: "Déclenche un calendrier juridique et plusieurs scénarios possibles."
  },
  monetary: {
    label: "Changer la monnaie",
    examples: "Euro, BCE, nouvelle monnaie",
    effect: "Modifie le cadre monétaire, bancaire, de change et de dette."
  },
  regulatory: {
    label: "Changer une règle",
    examples: "Interdiction, obligation, norme",
    effect: "Modifie les contraintes et comportements des acteurs."
  },
  nationalisation: {
    label: "Changer la propriété",
    examples: "Nationaliser une entreprise ou une infrastructure",
    effect: "Modifie les actifs publics, le financement et les revenus futurs."
  },
  energy: {
    label: "Changer le système énergétique",
    examples: "Nucléaire, renouvelables, fermeture ou construction de capacités",
    effect: "Modifie le parc énergétique, les prix, les investissements et les émissions."
  },
  infrastructure: {
    label: "Construire ou fermer des infrastructures",
    examples: "Rail, hôpitaux, prisons",
    effect: "Modifie le stock d'équipements et leur capacité dans le temps."
  },
  public_staffing: {
    label: "Changer les effectifs publics",
    examples: "Policiers, professeurs, soignants",
    effect: "Modifie les agents disponibles, la masse salariale et la capacité des services."
  },
  constitutional: {
    label: "Changer la Constitution",
    examples: "Proportionnelle, 49.3, règles institutionnelles",
    effect: "Modifie les règles de fonctionnement politique et juridique."
  },
  diplomatic: {
    label: "Changer la politique internationale",
    examples: "Alliance, non-alignement, accord bilatéral",
    effect: "Ouvre plusieurs scénarios géopolitiques plutôt qu'un résultat unique."
  },
  objective: {
    label: "Fixer un objectif",
    examples: "Neutralité carbone, plein emploi",
    effect: "Un objectif seul n'est pas une mesure : il faut des instruments concrets pour simuler son impact."
  }
};

export function detectMeasureType(policy){
  const text=policy.text.toLowerCase();
  const target=policy.target;

  if(target==="minimum_wage" || target==="retirement_age") return "parametric";
  if(target==="taxation" || target==="social_benefit") return "fiscal_social";
  if(target==="administrative_layer" || target==="administrative_reorganisation") return "administrative";
  if(target==="eu_exit") return "treaty";
  if(target==="nato_exit") return "treaty";
  if(target==="treaty_or_eu_rule") return text.includes("schengen") ? "treaty" : "european";
  if(target==="euro_exit") return "monetary";
  if(target==="constitutional_reform") return "constitutional";
  if(target==="privatisation_nationalisation") return "nationalisation";
  if(target==="foreign_policy") return "diplomatic";
  if(target==="energy") return "energy";

  if(target==="transport" && /(constru|ligne|gare|rail|infrastructure|autoroute)/.test(text)) return "infrastructure";
  if(target==="healthcare" && /(hôpital|hopital|lit|centre|infrastructure|constru)/.test(text)) return "infrastructure";
  if(target==="justice" && /(prison|tribunal|constru|infrastructure)/.test(text)) return "infrastructure";

  if(/(policiers?|professeurs?|enseignants?|soignants?|infirmiers?|médecins?|medecins?|agents publics?|fonctionnaires?)/.test(text)
     && /(créer|recruter|supprimer|réduire|augmenter|embaucher)/.test(text)) return "public_staffing";

  if(target==="public_spending" || /(milliards?|millions?).*(par an|annuel|budget)/.test(text)) return "budgetary";
  if(target==="media_regulation" || target==="digital_policy" || /(interdire|obliger|norme|réglement|reglement)/.test(text)) return "regulatory";
  if(target==="public_service") return "budgetary";
  if(target==="environment" && /(neutralité|objectif|atteindre|réduire de \d+%)/.test(text) && !/(taxe|interdire|investir|construire)/.test(text)) return "objective";
  if(target==="unknown" && /(objectif|neutralité|plein emploi|atteindre)/.test(text)) return "objective";
  if(target==="security" || target==="education" || target==="healthcare" || target==="justice" || target==="housing" || target==="defence" || target==="transport") return "regulatory";

  return "regulatory";
}
