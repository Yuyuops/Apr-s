import argparse
import json

from policy_engine.compiler import compile_measure
from policy_engine.schema import SourceRef
from simulation.engine import simulate_policy


def main():
    parser = argparse.ArgumentParser(description="Après MVP policy simulation")
    parser.add_argument("--text", required=True, help="Policy measure text")
    parser.add_argument("--horizon", type=int, default=12, help="Simulation horizon in months")
    args = parser.parse_args()

    source = SourceRef(
        organisation="SYNTHETIC",
        document="CLI input",
        version="runtime",
        url="https://example.invalid/runtime-input",
    )
    policy = compile_measure(policy_id="runtime-1", text=args.text, source=source)
    result = simulate_policy(policy, args.horizon)

    payload = {
        "policy": {
            "target": policy.target,
            "action": policy.action,
            "value": policy.value,
            "unit": policy.unit,
            "evidence_class": policy.evidence_class.value,
            "unresolved": policy.unresolved,
        },
        "simulation": result.to_dict(),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
