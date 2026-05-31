from datawatcher.core.base_audit import (
    BaseAudit
)

from datawatcher.core.audit_result import (
    AuditResult
)


class ShapeAudit(BaseAudit):

    audit_name = "shape_audit"

    category = "structural"

    MIN_ROWS = 100

    MIN_COLUMNS = 2

    def run(
        self,
        dataset,
        context=None
    ):

        rows = dataset.df.shape[0]

        columns = dataset.df.shape[1]

        findings = {
            "rows": rows,
            "columns": columns
        }

        recommendations = []

        # Validation logic
        passed = True

        if rows < self.MIN_ROWS:

            passed = False

            recommendations.append(
                "Dataset contains too few rows for reliable ML training."
            )

        if columns < self.MIN_COLUMNS:

            passed = False

            recommendations.append(
                "Dataset contains too few columns."
            )

        # Severity logic
        if rows == 0 or columns == 0:

            severity = "CRITICAL"

        elif rows < self.MIN_ROWS:

            severity = "HIGH"

        elif columns < self.MIN_COLUMNS:

            severity = "MEDIUM"

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