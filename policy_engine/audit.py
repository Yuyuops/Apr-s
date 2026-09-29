from collections import Counter
from .schema import PolicyObject


def audit(policies: list[PolicyObject]) -> dict:
    total = len(policies)
    traceable = sum(p.traceable for p in policies)
    classified = sum(p.target != "unknown" for p in policies)
    gaps = Counter(gap for p in policies for gap in p.unresolved)
    capabilities = Counter(cap for p in policies for cap in p.required_capabilities)
    return {
        "measures": total,
        "traceable_pct": round(100 * traceable / total, 1) if total else 0.0,
        "classified_pct": round(100 * classified / total, 1) if total else 0.0,
        "gaps": dict(gaps),
        "required_capabilities": dict(capabilities),
    }
