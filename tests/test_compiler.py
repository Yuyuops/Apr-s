from policy_engine.compiler import compile_measure
from policy_engine.schema import EvidenceClass, SourceRef

SOURCE = SourceRef("test", "fixture", "1", "https://example.invalid/source")


def test_unknown_measure_becomes_gap_not_guess():
    p = compile_measure(policy_id="x", text="Créer quelque chose de totalement inconnu", source=SOURCE)
    assert p.target == "unknown"
    assert p.evidence_class == EvidenceClass.UNKNOWN
    assert "unsupported_policy_target" in p.unresolved


def test_region_removal_requires_competence_destination():
    p = compile_measure(policy_id="x", text="Supprimer les régions", source=SOURCE)
    assert p.target == "administrative_layer"
    assert "destination_of_transferred_competences" in p.unresolved


def test_eu_exit_is_scenario_not_deterministic_prediction():
    p = compile_measure(policy_id="x", text="Sortie de l'Union européenne", source=SOURCE)
    assert p.evidence_class == EvidenceClass.SCENARIO_ONLY
    assert "international_treaty_exit" in p.required_capabilities
