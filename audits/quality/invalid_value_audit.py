from datawatcher.core.base_audit import (
    BaseAudit
)

from datawatcher.core.audit_result import (
    AuditResult
)

from datawatcher.utils.severity import (
    calculate_severity
)

from datawatcher.utils.thresholds import (
    INVALID_VALUE_THRESHOLDS
)

from datawatcher.utils.recommendations import (
    invalid_value_recommendation
)


NON_NEGATIVE_KEYWORDS = [
    "age",
    "salary",
    "income",
    "charges",
    "amount",
    "quantity",
    "count",
    "tenure"
]


class InvalidValueAudit(BaseAudit):

    audit_name = "invalid_value_audit"

    category = "quality"

    def run(
        self,
        dataset,
        context=None
    ):

        df = dataset.df

        invalid_columns = {}

        total_invalid = 0

        for column in df.columns:

            column_lower = column.lower()

            if not any(
                keyword in column_lower
                for keyword in NON_NEGATIVE_KEYWORDS
            ):
                continue

            if not (
                df[column]
                .dtype.kind
                in "if"
            ):
                continue

            invalid_count = int(
                (df[column] < 0).sum()
            )

            if invalid_count > 0:

                invalid_columns[column] = (
                    invalid_count
                )

                total_invalid += (
                    invalid_count
                )

        findings = {
            "invalid_column_count":
                len(invalid_columns),

            "invalid_columns":
                invalid_columns,

            "total_invalid_values":
                total_invalid
        }

        passed = (
            total_invalid == 0
        )

        severity = calculate_severity(
            value=total_invalid,
            low_threshold=
            INVALID_VALUE_THRESHOLDS[
                "low"
            ],
            medium_threshold=
            INVALID_VALUE_THRESHOLDS[
                "medium"
            ]
        )

        recommendations = [
            invalid_value_recommendation(
                total_invalid
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