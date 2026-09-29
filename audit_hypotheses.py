import json
from pathlib import Path

from policy_engine.compiler import RULES

REGISTRY = Path("data/hypotheses_registry.json")


def main():
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    covered_targets = {
        target
        for case in registry["cases"]
        for target in case.get("targets", [])
    }
    compiler_targets = {target for target, _ in RULES}
    missing = sorted(compiler_targets - covered_targets)

    incomplete_cases = sorted(
        case["id"]
        for case in registry["cases"]
        if not case.get("label")
        or not case.get("evidence")
        or "required_details" not in case
        or "affected_variables" not in case
    )

    print("APRÈS — HYPOTHESIS REGISTRY AUDIT")
    print(f"cases: {len(registry['cases'])}")
    print(f"interactions: {len(registry['interactions'])}")
    print(f"horizons: {len(registry['horizon_method'])}")
    print(f"exogenous_variables: {len(registry['exogenous_variables'])}")
    print(f"compiler_targets: {len(compiler_targets)}")
    print(f"missing_compiler_targets: {missing}")
    print(f"incomplete_cases: {incomplete_cases}")

    if missing or incomplete_cases:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
