from policy_engine.audit import audit
from policy_engine.compiler import compile_measure
from policy_engine.schema import SourceRef

DEMO = [
    "Porter le SMIC à 2 000 euros brut",
    "Sortie de l'Union européenne",
    "Sortie de l'OTAN",
    "Supprimer les régions",
]

source = SourceRef(
    organisation="DEMO",
    document="MVP smoke test",
    version="0",
    url="https://example.invalid/not-a-political-source",
)

policies = [
    compile_measure(policy_id=f"demo-{i}", text=text, source=source)
    for i, text in enumerate(DEMO, start=1)
]

if __name__ == "__main__":
    result = audit(policies)
    print("APRÈS — POLICY CAPABILITY AUDIT")
    for key, value in result.items():
        print(f"{key}: {value}")
