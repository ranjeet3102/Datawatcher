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

                results.append({
                    "audit_name": audit.audit_name,
                    "status": "failed",
                    "error": str(e)
                })

        return results