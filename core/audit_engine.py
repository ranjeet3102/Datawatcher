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

                # Use SimpleNamespace so attribute access (result.category,
                # result.audit_name, etc.) works the same as a real result object.
                results.append(
                    SimpleNamespace(
                        audit_name=audit.audit_name,
                        category="error",
                        passed=False,
                        severity="critical",
                        findings={"error": str(e)},
                        status="failed",
                    )
                )

        return results