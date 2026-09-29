from policy_engine.audit import audit
from policy_engine.compiler import compile_measure
from policy_engine.schema import SourceRef

S = SourceRef("fixture", "fixture", "1", "https://example.invalid")


def test_audit_reports_coverage_and_gaps():
    policies = [
        compile_measure(policy_id="1", text="Sortir de l'Union européenne", source=S),
        compile_measure(policy_id="2", text="Mesure inconnue sans modèle", source=S),
    ]
    result = audit(policies)
    assert result["measures"] == 2
    assert result["traceable_pct"] == 100.0
    assert result["classified_pct"] == 50.0
    assert result["gaps"]["unsupported_policy_target"] == 1
