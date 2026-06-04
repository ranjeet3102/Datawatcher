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


class BMIRangeAudit(BaseAudit):

    audit_name = (
        "bmi_range_audit"
    )

    category = "healthcare"

    BMI_COLUMN_KEYWORDS = [

        "bmi",

        "body_mass_index"
    ]

    def run(
        self,
        dataset,
        context=None
    ):

        df = dataset.df

        bmi_column = None

        for column in df.columns:

            if (
                column.lower()
                in self.BMI_COLUMN_KEYWORDS
            ):

                bmi_column = column

                break

        if bmi_column is None:

            return AuditResult(

                audit_name=
                self.audit_name,

                category=
                self.category,

                passed=True,

                severity="INFO",

                findings={
                    "message":
                    "No BMI column detected."
                },

                recommendations=[
                    "No BMI validation performed."
                ]
            )

        invalid_bmi_mask = (

            (df[bmi_column] < 10)

            |

            (df[bmi_column] > 70)

        )

        invalid_bmi_count = int(
            invalid_bmi_mask.sum()
        )

        invalid_bmi_percentage = (
            calculate_percentage(
                invalid_bmi_count,
                len(df)
            )
        )

        findings = {

            "bmi_column":
                bmi_column,

            "total_rows":
                len(df),

            "invalid_bmi_count":
                invalid_bmi_count,

            "invalid_bmi_percentage":
                invalid_bmi_percentage
        }

        severity = (
            calculate_severity(
                value=
                invalid_bmi_percentage,

                low_threshold=1,

                medium_threshold=5
            )
        )

        passed = (
            invalid_bmi_count == 0
        )

        recommendations = []

        if (
            invalid_bmi_count == 0
        ):

            recommendations.append(
                "All BMI values are within the valid range."
            )

        else:

            recommendations.append(
                "Invalid BMI values detected. "
                "Review patient measurements."
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