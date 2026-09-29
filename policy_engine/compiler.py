from .schema import EvidenceClass, PolicyObject, SourceRef

KEYWORDS = {
    "minimum_wage": ("smic", "minimum wage"),
    "eu_exit": ("sortie de l'union européenne", "quitter l'union européenne", "frexit"),
    "nato_exit": ("sortie de l'otan", "quitter l'otan"),
    "administrative_layer": ("supprimer les régions", "suppression des régions"),
}

CAPABILITIES = {
    "minimum_wage": ["tax_benefit_rules", "labour_market", "macroeconomy"],
    "eu_exit": ["international_treaty_exit", "trade_regime", "public_finance", "macroeconomy"],
    "nato_exit": ["international_treaty_exit", "defence_posture"],
    "administrative_layer": ["administrative_layer_removal", "competence_transfer", "public_finance"],
}


def compile_measure(*, policy_id: str, text: str, source: SourceRef) -> PolicyObject:
    lowered = text.lower()
    target = "unknown"
    for candidate, words in KEYWORDS.items():
        if any(word in lowered for word in words):
            target = candidate
            break

    unresolved: list[str] = []
    evidence = EvidenceClass.UNKNOWN
    if target != "unknown":
        evidence = EvidenceClass.MODELISABLE
    else:
        unresolved.append("unsupported_policy_target")

    if target in {"eu_exit", "nato_exit"}:
        evidence = EvidenceClass.SCENARIO_ONLY
    if target == "administrative_layer":
        unresolved.append("destination_of_transferred_competences")

    return PolicyObject(
        policy_id=policy_id,
        source=source,
        text=text,
        action="SET" if target == "minimum_wage" else "STRUCTURAL_CHANGE",
        target=target,
        required_capabilities=CAPABILITIES.get(target, []),
        evidence_class=evidence,
        unresolved=unresolved,
    )
