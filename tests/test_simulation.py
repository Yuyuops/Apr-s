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


def test_horizon_uncertainty_increases():
    p = compile_("Augmenter les dépenses publiques de 1 milliard d'euros par an")
    assert simulate_policy(p, 1).downstream_uncertainty == "low"
    assert simulate_policy(p, 12).downstream_uncertainty == "medium"
    assert simulate_policy(p, 24).downstream_uncertainty == "high"
    assert simulate_policy(p, 60).downstream_uncertainty == "very_high"


def test_fiscal_baseline_snapshot_is_ceteris_paribus():
    from simulation.engine import apply_fiscal_baseline

    baseline = {
        "id": "france_2025_insee",
        "period": "2025",
        "gdp_eur": 2_991_100_000_000,
        "public_deficit_eur": 152_500_000_000,
    }
    p = compile_("Augmenter les dépenses publiques de 12 milliards d'euros par an")
    r = simulate_policy(p, 12)
    snapshot = apply_fiscal_baseline(r, baseline)
    assert snapshot["annual_public_deficit_delta_eur"] == 12_000_000_000
    assert snapshot["annual_public_deficit_after_direct_effect_eur"] == 164_500_000_000


def test_fiscal_baseline_cumulative_impact_changes_with_horizon():
    from simulation.engine import apply_fiscal_baseline

    baseline = {
        "id": "france_2025_insee",
        "period": "2025",
        "gdp_eur": 2_991_100_000_000,
        "public_deficit_eur": 152_500_000_000,
    }
    p = compile_("Augmenter les dépenses publiques de 12 milliards d'euros par an")

    six = apply_fiscal_baseline(simulate_policy(p, 6), baseline)
    sixty = apply_fiscal_baseline(simulate_policy(p, 60), baseline)

    assert six["cumulative_public_deficit_delta_eur"] == 6_000_000_000
    assert sixty["cumulative_public_deficit_delta_eur"] == 60_000_000_000
    assert sixty["cumulative_debt_impact_pct_gdp"] > six["cumulative_debt_impact_pct_gdp"]
