import re
from .schema import EvidenceClass, PolicyObject, SourceRef

RULES = [
    ("minimum_wage", ("smic", "salaire minimum")),
    ("retirement_age", ("retraite à", "âge de départ")),
    ("taxation", ("impôt", "taxe", "cotisation", "prélèvement obligatoire")),
    ("public_spending", ("dépenses publiques", "financer")),
    ("social_benefit", ("minima sociaux", "allocation", "aide sociale")),
    ("healthcare", ("hôpital", "désert médical", "santé", "médicament")),
    ("education", ("éducation", "école", "enseignement")),
    ("justice", ("justice", "sanctionner")),
    ("immigration", ("immigration", "asile", "clandestin", "étranger")),
    ("media_regulation", ("médias", "media")),
    ("environment", ("écologique", "transition", "incendie", "littoral")),
    ("transport", ("rail", "transport")),
    ("administrative_layer", ("supprimer les régions", "suppression des régions")),
    ("administrative_reorganisation", ("organismes administratifs", "opérateurs d'état", "administration territoriale")),
    ("eu_exit", ("sortir de l'union européenne", "sortie de l'union européenne", "frexit")),
    ("euro_exit", ("sortir de l'euro", "sortie de l'euro")),
    ("nato_exit", ("sortir de l'otan", "sortie de l'otan", "quitter l'otan")),
    ("treaty_or_eu_rule", ("schengen", "juges européens", "traités européens")),
    ("constitutional_reform", ("assemblée constituante", "6e république", "constitution", "référendum")),
    ("public_service", ("service public", "services publics")),
    ("privatisation_nationalisation", ("privatisation", "nationalisation")),
    ("foreign_policy", ("politique étrangère", "aides au développement")),
    ("digital_policy", ("numérique",)),
    ("security", ("police", "sécurité", "délinquance")),
    ("housing", ("logement", "logements")),
    ("defence", ("défense", "armée", "militaire")),
    ("energy", ("énergie", "renouvelable", "nucléaire")),
]

CAPABILITIES = {
    "minimum_wage": ["tax_benefit_rules", "labour_market", "macroeconomy"],
    "retirement_age": ["pension_system", "labour_market", "public_finance"],
    "taxation": ["tax_benefit_rules", "public_finance", "distribution"],
    "public_spending": ["public_finance", "macroeconomy"],
    "social_benefit": ["tax_benefit_rules", "take_up_model", "public_finance"],
    "healthcare": ["health_system", "public_finance", "regional_access"],
    "education": ["education_system", "public_finance"],
    "justice": ["justice_system"],
    "immigration": ["migration_system", "public_finance", "labour_market"],
    "media_regulation": ["media_market", "regulatory_change"],
    "environment": ["environment_energy", "public_finance"],
    "transport": ["transport_system", "environment_energy", "public_finance"],
    "administrative_layer": ["administrative_layer_removal", "competence_transfer", "public_finance"],
    "administrative_reorganisation": ["administrative_reorganisation", "competence_transfer", "public_finance"],
    "eu_exit": ["international_treaty_exit", "trade_regime", "public_finance", "macroeconomy"],
    "euro_exit": ["monetary_regime_change", "banking_finance", "macroeconomy"],
    "nato_exit": ["international_treaty_exit", "defence_posture"],
    "treaty_or_eu_rule": ["international_legal_change", "scenario_branching"],
    "constitutional_reform": ["constitutional_change", "institutional_graph"],
    "public_service": ["public_finance", "public_service_capacity"],
    "privatisation_nationalisation": ["asset_valuation", "public_finance", "sector_model"],
    "foreign_policy": ["international_relations_scenarios"],
    "digital_policy": ["digital_economy", "regulatory_change"],
    "security": ["security_system", "public_finance"],
    "housing": ["housing_market", "public_finance", "distribution"],
    "defence": ["defence_posture", "public_finance"],
    "energy": ["environment_energy", "energy_system", "public_finance"],
}

SCENARIO_TARGETS = {
    "eu_exit", "euro_exit", "nato_exit", "treaty_or_eu_rule",
    "constitutional_reform", "foreign_policy"
}


def _extract_numeric(text: str):
    match = re.search(r"(\d[\d\s]*(?:[,.]\d+)?)\s*(%|euros?|€|milliards?|millions?)?", text.lower())
    if not match:
        return None, None
    raw = match.group(1).replace(" ", "").replace(",", ".")
    try:
        value = float(raw)
        if value.is_integer():
            value = int(value)
    except ValueError:
        return None, None
    return value, match.group(2)


def compile_measure(*, policy_id: str, text: str, source: SourceRef) -> PolicyObject:
    lowered = text.lower()
    target = "unknown"
    for candidate, words in RULES:
        if any(word in lowered for word in words):
            target = candidate
            break

    value, unit = _extract_numeric(text)
    unresolved: list[str] = []
    evidence = EvidenceClass.MODELISABLE if target != "unknown" else EvidenceClass.UNKNOWN

    if target == "unknown":
        unresolved.append("unsupported_policy_target")
    if target in SCENARIO_TARGETS:
        evidence = EvidenceClass.SCENARIO_ONLY
    if target == "administrative_layer":
        unresolved.append("destination_of_transferred_competences")
    if target in {"eu_exit", "euro_exit"}:
        unresolved.append("post_exit_regime_not_specified")
    if target == "taxation" and value is None:
        unresolved.append("tax_parameter_not_quantified")
    if target in {"public_service", "healthcare", "education"} and value is None:
        unresolved.append("implementation_scale_not_quantified")

    action = "SET" if value is not None else "STRUCTURAL_CHANGE"
    return PolicyObject(
        policy_id=policy_id, source=source, text=text, action=action,
        target=target, value=value, unit=unit,
        required_capabilities=CAPABILITIES.get(target, []),
        evidence_class=evidence, unresolved=unresolved,
    )
