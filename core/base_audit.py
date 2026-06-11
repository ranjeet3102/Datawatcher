from abc import ABC, abstractmethod

from datawatcher.core.audit_result import (
    AuditResult
)


class BaseAudit(ABC):
  

    audit_name = "base_audit"

    category = "general"

    @abstractmethod
    def run(
        self,
        dataset,
        context=None
    ) -> AuditResult:
    
        pass