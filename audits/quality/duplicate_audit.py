from datawatcher.core.base_audit import BaseAudit
from datawatcher.core.audit_result import AuditResult

from datawatcher.utils.percentages import (
    calculate_percentage
)

from datawatcher.utils.severity import (
    calculate_severity
)

from datawatcher.utils.thresholds import (
    DUPLICATE_THRESHOLDS
)

from datawatcher.utils.recommendations import (
    duplicate_recommendation
)


class DuplicateAudit(BaseAudit):

    audit_name = "duplicate_audit"

    category = "quality"

    def run(
        self,
        dataset,
        context=None
    ):

        df = dataset.df

        total_rows = len(df)

        duplicate_rows = int(
            df.duplicated().sum()
        )

        duplicate_percentage = (
            calculate_percentage(
                duplicate_rows,
                total_rows
            )
        )

        findings = {
            "total_rows": total_rows,
            "duplicate_rows": duplicate_rows,
            "duplicate_percentage": duplicate_percentage
        }

        passed = (
            duplicate_percentage
            < DUPLICATE_THRESHOLDS["medium"]
        )

        severity = calculate_severity(
            value=duplicate_percentage,
            low_threshold=DUPLICATE_THRESHOLDS["low"],
            medium_threshold=DUPLICATE_THRESHOLDS["medium"]
        )

        recommendations = [
            duplicate_recommendation(
                duplicate_percentage
            )
        ]

        return AuditResult(
            audit_name=self.audit_name,
            category=self.category,
            passed=passed,
            severity=severity,
            findings=findings,
            recommendations=recommendations
        )