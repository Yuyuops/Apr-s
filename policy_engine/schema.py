from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EvidenceClass(str, Enum):
    CALCULABLE = "calculable"
    MODELISABLE = "modelisable"
    SCENARIO_ONLY = "scenario_only"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class SourceRef:
    organisation: str
    document: str
    version: str
    url: str
    quote: str = ""


@dataclass
class PolicyObject:
    policy_id: str
    source: SourceRef
    text: str
    action: str
    target: str
    value: Any = None
    unit: str | None = None
    timeline: str | None = None
    domains: list[str] = field(default_factory=list)
    prerequisites: list[str] = field(default_factory=list)
    affected_variables: list[str] = field(default_factory=list)
    required_capabilities: list[str] = field(default_factory=list)
    evidence_class: EvidenceClass = EvidenceClass.UNKNOWN
    assumptions: list[str] = field(default_factory=list)
    unresolved: list[str] = field(default_factory=list)

    @property
    def traceable(self) -> bool:
        return bool(self.source.url and self.source.version and self.text)
