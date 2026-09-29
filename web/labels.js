export const TARGET_LABELS = {
  minimum_wage: "Salaire minimum",
  retirement_age: "Retraites",
  taxation: "Impôts et cotisations",
  public_spending: "Dépenses publiques",
  social_benefit: "Aides et prestations",
  healthcare: "Santé",
  education: "Éducation",
  justice: "Justice",
  immigration: "Immigration et asile",
  media_regulation: "Médias",
  environment: "Environnement",
  transport: "Transports",
  administrative_layer: "Organisation territoriale",
  administrative_reorganisation: "Réorganisation de l'administration",
  eu_exit: "Sortie de l'Union européenne",
  euro_exit: "Changement de monnaie / sortie de l'euro",
  nato_exit: "Sortie de l'OTAN",
  treaty_or_eu_rule: "Règles européennes / Schengen",
  constitutional_reform: "Réforme des institutions",
  public_service: "Services publics",
  privatisation_nationalisation: "Nationalisation / privatisation",
  foreign_policy: "Politique étrangère",
  digital_policy: "Numérique",
  security: "Police et sécurité",
  housing: "Logement",
  defence: "Défense",
  energy: "Énergie",
  unknown: "Mesure non reconnue"
};

export const ACTION_LABELS = {
  INCREASE: "Augmentation",
  DECREASE: "Baisse",
  SET: "Nouveau niveau fixé",
  STRUCTURAL_CHANGE: "Changement de règles ou d'organisation"
};

export const CONFIDENCE_LABELS = {
  high_for_accounting_effect_only: "Calcul direct fiable",
  high_for_accounting_effects_only: "Calculs directs fiables",
  scenario_only: "Scénario uniquement",
  unknown: "Pas encore calculable"
};

export const UNCERTAINTY_LABELS = {
  low: "Faible",
  medium: "Moyenne",
  high: "Élevée",
  very_high: "Très élevée",
  low_for_direct_effects: "Faible pour les effets directs"
};

export const EVIDENCE_LABELS = {
  calculable: "Calcul direct",
  modelisable: "Estimation par modèle",
  calculable_then_modelisable: "Calcul direct + estimation",
  modelisable_scenario: "Estimation + scénarios",
  scenario_only: "Scénarios uniquement",
  scenario_only_then_calculable: "Scénarios puis calcul direct",
  unsupported: "Pas encore calculable"
};

export const MODEL_LABELS = {
  tax_benefit_rules: "Règles d'impôts et d'aides",
  labour_market: "Emploi et salaires",
  macroeconomy: "Économie globale",
  pension_system: "Retraites",
  public_finance: "Budget de l'État",
  distribution: "Répartition des revenus",
  take_up_model: "Recours aux aides",
  health_system: "Système de santé",
  regional_access: "Accès local aux services",
  education_system: "Système éducatif",
  justice_system: "Justice",
  migration_system: "Immigration et démographie",
  media_market: "Marché des médias",
  regulatory_change: "Effet des nouvelles règles",
  environment_energy: "Énergie et climat",
  transport_system: "Transports",
  administrative_layer_removal: "Suppression d'un niveau administratif",
  competence_transfer: "Transfert des missions et moyens",
  administrative_reorganisation: "Réorganisation administrative",
  international_treaty_exit: "Sortie d'un traité international",
  trade_regime: "Commerce extérieur",
  monetary_regime_change: "Changement de monnaie",
  banking_finance: "Banques et finance",
  defence_posture: "Organisation de la défense",
  international_legal_change: "Changement de règles internationales",
  scenario_branching: "Scénarios alternatifs",
  constitutional_change: "Réforme constitutionnelle",
  institutional_graph: "Organisation des institutions",
  public_service_capacity: "Capacité des services publics",
  asset_valuation: "Valeur des entreprises et actifs",
  sector_model: "Effets dans le secteur concerné",
  international_relations_scenarios: "Scénarios internationaux",
  digital_economy: "Économie numérique",
  security_system: "Police et sécurité",
  housing_market: "Marché du logement",
  energy_system: "Système énergétique",
  policy_interaction_model: "Effets combinés entre les mesures"
};

export const VARIABLE_LABELS = {
  salaires: "Salaires",
  cout_travail: "Coût du travail",
  revenu_menages: "Revenu des ménages",
  emploi: "Emploi",
  recettes_publiques: "Recettes publiques",
  depenses_retraites: "Dépenses de retraite",
  emploi_seniors: "Emploi des seniors",
  cotisations: "Cotisations",
  revenu_disponible: "Pouvoir d'achat après impôts et aides",
  consommation: "Consommation",
  pauvrete: "Pauvreté",
  capacite_soins: "Capacité de soins",
  temps_acces: "Temps d'accès aux soins",
  depenses_sante: "Dépenses de santé",
  taille_classes: "Taille des classes",
  effectifs_publics: "Effectifs publics",
  depenses_education: "Dépenses d'éducation",
  delais_justice: "Délais de justice",
  stock_affaires: "Affaires en attente",
  capacite_justice: "Capacité de la justice",
  effectifs_police: "Effectifs de police",
  depenses_securite: "Dépenses de sécurité",
  capacite_operationnelle: "Capacité opérationnelle",
  migration_nette: "Solde migratoire",
  population_active: "Population active",
  logement: "Logement",
  finances_publiques: "Finances publiques",
  structure_marche_medias: "Structure du marché des médias",
  cout_conformite: "Coût de mise en conformité",
  gouvernance_medias: "Gouvernance des médias",
  offre_logement: "Nombre de logements disponibles",
  prix_logement: "Prix des logements",
  loyers: "Loyers",
  depenses_publiques: "Dépenses publiques",
  emissions_CO2: "Émissions de CO₂",
  pollution: "Pollution",
  mix_energetique: "Mix énergétique",
  prix_energie: "Prix de l'énergie",
  investissement: "Investissement",
  investissement_public: "Investissement public",
  mobilite: "Mobilité",
  organisation_etat: "Organisation de l'État",
  competences: "Répartition des compétences",
  capacite_service_public: "Capacité des services publics",
  commerce: "Commerce extérieur",
  budget_public: "Budget public",
  reglementation: "Réglementation",
  PIB: "PIB",
  taux: "Taux d'intérêt",
  inflation: "Inflation",
  change: "Taux de change",
  banques: "Banques",
  dette: "Dette",
  depenses_defense: "Dépenses de défense",
  posture_defense: "Organisation de la défense",
  relations_internationales: "Relations internationales",
  frontieres: "Contrôles aux frontières",
  administration: "Administration",
  institutions: "Institutions",
  calendrier_legislatif: "Calendrier des réformes",
  actifs_publics: "Actifs publics",
  dividendes: "Dividendes",
  investissement_sectoriel: "Investissement du secteur",
  effectifs_defense: "Effectifs de défense",
  capacite_militaire: "Capacité militaire",
  investissement_numerique: "Investissement numérique",
  services_numeriques: "Services numériques"
};

export const EXOGENOUS_LABELS = {
  taux_BCE: "Taux d'intérêt de la BCE",
  croissance_mondiale: "Croissance mondiale",
  prix_petrole: "Prix du pétrole",
  prix_gaz: "Prix du gaz",
  EUR_USD: "Taux de change euro / dollar",
  demographie: "Évolution de la population",
  commerce_mondial: "Commerce mondial",
  contexte_UE: "Décisions et contexte de l'Union européenne"
};

export const SOURCE_STATUS_LABELS = {
  current_official_source: "source officielle actuelle",
  current: "source actuelle",
  current_base: "base actuelle",
  historical_test: "ancien programme utilisé pour tester le simulateur",
  synthetic: "exemple fictif",
  synthetic_fixture: "exemple fictif de test"
};

export const SCENARIO_LABELS = {
  relation_future_non_precisee: "Relation future avec l'UE non précisée",
  relation_type_marche_integre: "Accès proche du marché unique",
  accord_commercial: "Accord commercial négocié",
  regime_OMC: "Relations commerciales selon les règles de l'OMC",
  nouvelle_monnaie_non_precisee: "Nouvelle monnaie non précisée",
  conversion_unitaire: "Conversion des contrats avec un taux unique",
  conversion_differentiee: "Conversion différente selon les contrats"
};

export function humanize(value, dictionary={}){
  if(value==null) return "";
  if(dictionary[value]) return dictionary[value];
  return String(value)
    .replaceAll("_"," ")
    .replace(/\b\w/g,c=>c.toUpperCase());
}
