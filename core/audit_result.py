from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass
class AuditResult:
    """
    Standardized audit output object.
    """

    audit_name: str

    category: str

    passed: bool

    severity: str

    findings: Dict[str, Any]

    recommendations: List[str] = field(
        default_factory=list
    )