import csv
from collections import Counter
from pathlib import Path

from policy_engine.audit import audit
from policy_engine.compiler import compile_measure
from policy_engine.schema import SourceRef

CORPUS = Path("programs/seed_corpus.csv")


def load():
    policies = []
    with CORPUS.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            source = SourceRef(
                organisation=row["organisation"],
                document=row["document"],
                version=row["version"],
                url=row["url"],
            )
            policies.append(
                compile_measure(
                    policy_id=row["policy_id"],
                    text=row["text"],
                    source=source,
                )
            )
    return policies


if __name__ == "__main__":
    policies = load()
    result = audit(policies)
    targets = Counter(p.target for p in policies)
    evidence = Counter(p.evidence_class.value for p in policies)
    synthetic_count = sum(
        1
        for line in CORPUS.read_text(encoding="utf-8").splitlines()[1:]
        if '"synthetic_fixture"' in line
    )

    print("APRÈS — POLICY CAPABILITY AUDIT")
    print(f"measures: {len(policies)}")
    print(f"synthetic_fixtures: {synthetic_count}")
    print(f"traceable: {result['traceable_pct']}%")
    print(f"classified: {result['classified_pct']}%")
    print(f"targets: {dict(targets)}")
    print(f"evidence: {dict(evidence)}")
    print(f"gaps: {result['gaps']}")
    print(f"required_capabilities: {result['required_capabilities']}")
