from policy_engine.compiler import compile_measure
from policy_engine.schema import SourceRef
from simulation.engine import simulate_policy, simulate_program

S = SourceRef("SYNTHETIC", "fixture", "1", "https://example.invalid")


def compile_(text):
    return compile_measure(policy_id="x", text=text, source=S)


def test_annual_public_spending_direct_effect_scales_with_time():
    p = compile_("Augmenter les dépenses publiques de 12 milliards d'euros par an")
    r = simulate_policy(p, 6)
    assert r.direct_effects["annual_public_spending_delta_eur"] == 12_000_000_000
    assert r.direct_effects["cumulative_public_spending_delta_eur"] == 6_000_000_000


def test_tax_cut_reduces_public_revenue():
    p = compile_("Réduire les impôts de 2 milliards d'euros par an")
    r = simulate_policy(p, 12)
    assert r.direct_effects["annual_public_revenue_delta_eur"] == -2_000_000_000


def test_no_periodicity_means_no_invented_recurring_effect():
    p = compile_("Augmenter les dépenses publiques de 10 milliards d'euros")
    r = simulate_policy(p, 12)
    assert r.direct_effects == {}
    assert any("no annual periodicity" in a for a in r.assumptions)


def test_program_marks_interaction_model_as_missing():
    policies = [
        compile_("Augmenter les dépenses publiques de 1 milliard d'euros par an"),
        compile_("Réduire les impôts de 1 milliard d'euros par an"),
    ]
    r = simulate_program(policies, 12)
    assert "policy_interaction_model" in r.missing_capabilities
