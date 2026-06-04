from datawatcher.core.base_audit import (
    BaseAudit
)

from datawatcher.core.audit_result import (
    AuditResult
)

from datawatcher.utils.percentages import (
    calculate_percentage
)

from datawatcher.utils.severity import (
    calculate_severity
)


class AgeRangeAudit(BaseAudit):

    audit_name = (
        "age_range_audit"
    )

    category = "healthcare"

    AGE_COLUMN_KEYWORDS = [

        "age",

        "patient_age"
    ]

    def run(
        self,
        dataset,
        context=None
    ):

        df = dataset.df

        age_column = None

        for column in df.columns:

            if (
                column.lower()
                in self.AGE_COLUMN_KEYWORDS
            ):

                age_column = column

                break

        if age_column is None:

            return AuditResult(

                audit_name=
                self.audit_name,

                category=
                self.category,

                passed=True,

                severity="INFO",

                findings={
                    "message":
                    "No age column detected."
                },

                recommendations=[
                    "No age validation performed."
                ]
            )

        invalid_age_mask = (

            (df[age_column] < 0)

            |

            (df[age_column] > 120)

        )

        invalid_age_count = int(
            invalid_age_mask.sum()
        )

        invalid_age_percentage = (
            calculate_percentage(
                invalid_age_count,
                len(df)
            )
        )

        findings = {

            "age_column":
                age_column,

            "total_rows":
                len(df),

            "invalid_age_count":
                invalid_age_count,

            "invalid_age_percentage":
                invalid_age_percentage
        }

        severity = (
            calculate_severity(
                value=
                invalid_age_percentage,

                low_threshold=1,

                medium_threshold=5
            )
        )

        passed = (
            invalid_age_count == 0
        )

        recommendations = []

        if (
            invalid_age_count == 0
        ):

            recommendations.append(
                "All age values are within the valid range."
            )

        else:

            recommendations.append(
                "Invalid age values detected. "
                "Review patient age records."
            )

        return AuditResult(

            audit_name=
            self.audit_name,

            category=
            self.category,

            passed=
            passed,

            severity=
            severity,

            findings=
            findings,

            recommendations=
            recommendations
        )