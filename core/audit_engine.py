from types import SimpleNamespace


class AuditEngine:

    def __init__(
        self,
        registry
    ):

        self.registry = registry

    def run(
        self,
        dataset,
        context=None
    ):

        results = []

        for audit in (
            self.registry.get_audits()
        ):

            try:

                result = audit.run(
                    dataset,
                    context
                )

                results.append(result)

            except Exception as e:

                results.append(
                    SimpleNamespace(
                        audit_name=audit.audit_name,
                        category="error",
                        passed=False,
                        severity="critical",
                        findings={"error": str(e)},
                        recommendations=[],
                        status="failed",
                    )
                )

        return results