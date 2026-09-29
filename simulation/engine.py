from dataclasses import asdict, dataclass, field
from typing import Iterable

from policy_engine.schema import PolicyObject


@dataclass
class SimulationResult:
    horizon_months: int
    direct_effects: dict[str, float] = field(default_factory=dict)
    modeled_effects: dict[str, float] = field(default_factory=dict)
    scenario_notes: list[str] = field(default_factory=list)
    missing_capabilities: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    confidence: str = "unknown"
    downstream_uncertainty: str = "unknown"

    def to_dict(self) -> dict:
        return asdict(self)


def _horizon_uncertainty(horizon_months: int) -> str:
    if horizon_months <= 6:
        return "low"
    if horizon_months <= 12:
        return "medium"
    if horizon_months <= 24:
        return "high"
    return "very_high"


def _to_eur(value, unit: str | None) -> float | None:
    if value is None:
        return None
    if unit in {"€", "euro", "euros"}:
        return float(value)
    if unit in {"milliard", "milliards"}:
        return float(value) * 1_000_000_000
    if unit in {"million", "millions"}:
        return float(value) * 1_000_000
    return None


def _annual_amount(policy: PolicyObject) -> float | None:
    text = policy.text.lower()
    if not any(marker in text for marker in ("par an", "/an", "annuel", "annuelle")):
        return None
    return _to_eur(policy.value, policy.unit)


def simulate_policy(policy: PolicyObject, horizon_months: int) -> SimulationResult:
    if horizon_months <= 0:
        raise ValueError("horizon_months must be > 0")

    result = SimulationResult(
        horizon_months=horizon_months,
        downstream_uncertainty=_horizon_uncertainty(horizon_months),
    )
    result.missing_capabilities = list(dict.fromkeys(policy.required_capabilities))

    annual = _annual_amount(policy)
    sign = 1.0 if policy.action == "INCREASE" else -1.0 if policy.action == "DECREASE" else None

    if policy.target == "public_spending" and annual is not None and sign is not None:
        annual_delta = sign * annual
        result.direct_effects["annual_public_spending_delta_eur"] = annual_delta
        result.direct_effects["cumulative_public_spending_delta_eur"] = annual_delta * horizon_months / 12
        result.assumptions.append("Amount interpreted as an annual budget flow from explicit source wording.")
        result.confidence = "high_for_accounting_effect_only"
        result.missing_capabilities = [c for c in result.missing_capabilities if c != "public_finance"]

    elif policy.target == "taxation" and annual is not None and sign is not None:
        annual_delta = sign * annual
        result.direct_effects["annual_public_revenue_delta_eur"] = annual_delta
        result.direct_effects["cumulative_public_revenue_delta_eur"] = annual_delta * horizon_months / 12
        result.assumptions.append("Amount interpreted as an annual public-revenue flow from explicit source wording.")
        result.confidence = "high_for_accounting_effect_only"
        result.missing_capabilities = [c for c in result.missing_capabilities if c != "public_finance"]

    if policy.evidence_class.value == "scenario_only":
        result.scenario_notes.append(
            "This policy changes an institutional or external regime; downstream outcomes require explicit scenario branches."
        )
        if result.confidence == "unknown":
            result.confidence = "scenario_only"

    if policy.value is not None and annual is None and policy.unit in {
        "€", "euro", "euros", "million", "millions", "milliard", "milliards"
    }:
        result.assumptions.append(
            "A monetary amount was detected, but no annual periodicity was explicit; no recurring budget effect was invented."
        )

    return result


def simulate_program(policies: Iterable[PolicyObject], horizon_months: int) -> SimulationResult:
    policies = list(policies)
    total = SimulationResult(
        horizon_months=horizon_months,
        downstream_uncertainty=_horizon_uncertainty(horizon_months),
    )

    for policy in policies:
        one = simulate_policy(policy, horizon_months)
        for key, value in one.direct_effects.items():
            total.direct_effects[key] = total.direct_effects.get(key, 0.0) + value
        for key, value in one.modeled_effects.items():
            total.modeled_effects[key] = total.modeled_effects.get(key, 0.0) + value
        total.scenario_notes.extend(one.scenario_notes)
        total.assumptions.extend(one.assumptions)
        total.missing_capabilities.extend(one.missing_capabilities)

    total.missing_capabilities = list(dict.fromkeys(total.missing_capabilities))
    total.scenario_notes = list(dict.fromkeys(total.scenario_notes))
    total.assumptions = list(dict.fromkeys(total.assumptions))

    if len(policies) > 1:
        total.missing_capabilities.append("policy_interaction_model")
        total.missing_capabilities = list(dict.fromkeys(total.missing_capabilities))

    if total.direct_effects:
        total.confidence = "high_for_accounting_effects_only"
    elif total.scenario_notes:
        total.confidence = "scenario_only"

    return total


def apply_fiscal_baseline(result: SimulationResult, baseline: dict) -> dict | None:
    spending_delta = result.direct_effects.get("annual_public_spending_delta_eur")
    revenue_delta = result.direct_effects.get("annual_public_revenue_delta_eur")

    if spending_delta is None and revenue_delta is None:
        return None

    spending_delta = spending_delta or 0.0
    revenue_delta = revenue_delta or 0.0
    deficit_delta = spending_delta - revenue_delta
    baseline_deficit = float(baseline["public_deficit_eur"])
    gdp = float(baseline["gdp_eur"])
    new_deficit = baseline_deficit + deficit_delta

    return {
        "baseline_id": baseline["id"],
        "baseline_period": baseline["period"],
        "baseline_public_deficit_eur": baseline_deficit,
        "annual_public_deficit_delta_eur": deficit_delta,
        "annual_public_deficit_after_direct_effect_eur": new_deficit,
        "annual_public_deficit_after_direct_effect_pct_gdp": 100 * new_deficit / gdp,
        "assumption": "Ceteris paribus accounting snapshot: GDP and all non-measure flows are held constant.",
    }
