import re

from datawatcher.core.base_audit import (
    BaseAudit
)

from datawatcher.core.audit_result import (
    AuditResult
)


class SchemaConsistencyAudit(BaseAudit):

    audit_name = "schema_consistency_audit"

    category = "structural"

    VALID_COLUMN_PATTERN = r"^[a-z0-9_]+$"

    def run(
        self,
        dataset,
        context=None
    ):

        columns = dataset.df.columns.tolist()

        findings = {}

        recommendations = []

        duplicate_columns = []

        empty_columns = []

        invalid_columns = []

        # Duplicate column detection
        seen = set()

        for column in columns:

            if column in seen:

                duplicate_columns.append(
                    column
                )

            seen.add(column)

        # Empty column detection
        for column in columns:

            if not str(column).strip():

                empty_columns.append(
                    column
                )

        # Invalid naming detection
        for column in columns:

            if not re.match(
                self.VALID_COLUMN_PATTERN,
                str(column)
            ):

                invalid_columns.append(
                    column
                )

        findings["duplicate_columns"] = (
            duplicate_columns
        )

        findings["empty_columns"] = (
            empty_columns
        )

        findings["invalid_columns"] = (
            invalid_columns
        )

        findings["column_count"] = (
            len(columns)
        )

        # Validation logic
        passed = True

        if (
            duplicate_columns
            or empty_columns
            or invalid_columns
        ):

            passed = False

        # Severity logic
        if duplicate_columns:

            severity = "HIGH"

            recommendations.append(
                "Resolve duplicate column names."
            )

        elif empty_columns:

            severity = "HIGH"

            recommendations.append(
                "Remove or rename empty columns."
            )

        elif invalid_columns:

            severity = "MEDIUM"

            recommendations.append(
                "Normalize invalid column names."
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