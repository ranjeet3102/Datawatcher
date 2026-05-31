from datawatcher.core.base_audit import (
    BaseAudit
)

from datawatcher.core.audit_result import (
    AuditResult
)


class MemoryUsageAudit(BaseAudit):

    audit_name = "memory_usage_audit"

    category = "structural"

    WARNING_MEMORY_MB = 500

    CRITICAL_MEMORY_MB = 2000

    def run(
        self,
        dataset,
        context=None
    ):

        df = dataset.df

        total_memory_mb = (
            df.memory_usage(deep=True).sum()
            / (1024 * 1024)
        )

        column_memory = {}

        for column in df.columns:

            memory_mb = (
                df[column]
                .memory_usage(deep=True)
                / (1024 * 1024)
            )

            # column_memory[column] = round(
            #     memory_mb,
            #     2
            # )
            column_memory[column] = float(
            round(
              memory_mb,
                2
                     )
                )

        # findings = {
        #     "total_memory_mb": round(
        #         total_memory_mb,
        #         2
        #     ),
        #     "column_memory_mb": column_memory
        # }

        findings = {
        "total_memory_mb": float(
        round(
            total_memory_mb,
            2
        )
        ),
        "column_memory_mb": column_memory
        }

        recommendations = []

        # Validation logic
        passed = True

        if (
            total_memory_mb
            > self.CRITICAL_MEMORY_MB
        ):

            passed = False

            recommendations.append(
                "Dataset memory usage is extremely high."
            )

        # Severity logic
        if (
            total_memory_mb
            > self.CRITICAL_MEMORY_MB
        ):

            severity = "CRITICAL"

        elif (
            total_memory_mb
            > self.WARNING_MEMORY_MB
        ):

            severity = "HIGH"

            recommendations.append(
                "Consider optimizing dtypes or reducing dataset size."
            )

        else:

            severity = "LOW"

        return AuditResult(
            audit_name=self.audit_name,
            category=self.category,
            passed=passed,
            severity=severity,
            findings=findings,
            recommendations=recommendations
        )