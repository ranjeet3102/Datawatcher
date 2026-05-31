from abc import ABC, abstractmethod

from datawatcher.core.audit_result import (
    AuditResult
)


class BaseAudit(ABC):
    """
    Base interface for all audits.
    """

    audit_name = "base_audit"

    category = "general"

    @abstractmethod
    def run(
        self,
        dataset,
        context=None
    ) -> AuditResult:
        """
        Execute audit.
        """
        pass