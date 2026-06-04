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


class HeartRateAudit(BaseAudit):

    audit_name = (
        "heart_rate_audit"
    )

    category = "healthcare"

    HEART_RATE_KEYWORDS = [

        "heart_rate",

        "heartrate",

        "pulse",

        "pulse_rate"
    ]

    def run(
        self,
        dataset,
        context=None
    ):

        df = dataset.df

        heart_rate_column = None

        for column in df.columns:

            if (
                column.lower()
                in self.HEART_RATE_KEYWORDS
            ):

                heart_rate_column = column

                break

        if heart_rate_column is None:

            return AuditResult(

                audit_name=
                self.audit_name,

                category=
                self.category,

                passed=True,

                severity="INFO",

                findings={
                    "message":
                    "No heart rate column detected."
                },

                recommendations=[
                    "No heart rate validation performed."
                ]
            )

        invalid_mask = (

            (df[heart_rate_column] < 20)

            |

            (df[heart_rate_column] > 250)

        )

        invalid_count = int(
            invalid_mask.sum()
        )

        invalid_percentage = (
            calculate_percentage(
                invalid_count,
                len(df)
            )
        )

        findings = {

            "heart_rate_column":
                heart_rate_column,

            "total_rows":
                len(df),

            "invalid_heart_rate_count":
                invalid_count,

            "invalid_heart_rate_percentage":
                invalid_percentage
        }

        severity = (
            calculate_severity(
                value=
                invalid_percentage,

                low_threshold=1,

                medium_threshold=5
            )
        )

        passed = (
            invalid_count == 0
        )

        recommendations = []

        if (
            invalid_count == 0
        ):

            recommendations.append(
                "Heart rate values appear valid."
            )

        else:

            recommendations.append(
                "Invalid heart rate values detected. "
                "Review patient vital sign measurements."
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