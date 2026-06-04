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


class BloodPressureAudit(BaseAudit):

    audit_name = (
        "blood_pressure_audit"
    )

    category = "healthcare"

    SYSTOLIC_KEYWORDS = [

        "systolic",

        "systolic_bp",

        "systolic_pressure"
    ]

    DIASTOLIC_KEYWORDS = [

        "diastolic",

        "diastolic_bp",

        "diastolic_pressure"
    ]

    def run(
        self,
        dataset,
        context=None
    ):

        df = dataset.df

        systolic_column = None
        diastolic_column = None

        for column in df.columns:

            column_lower = (
                column.lower()
            )

            if (
                column_lower
                in self.SYSTOLIC_KEYWORDS
            ):

                systolic_column = column

            if (
                column_lower
                in self.DIASTOLIC_KEYWORDS
            ):

                diastolic_column = column

        if (
            systolic_column is None
            or
            diastolic_column is None
        ):

            return AuditResult(

                audit_name=
                self.audit_name,

                category=
                self.category,

                passed=True,

                severity="INFO",

                findings={
                    "message":
                    "Blood pressure columns not detected."
                },

                recommendations=[
                    "No blood pressure validation performed."
                ]
            )

        invalid_mask = (

            (
                df[systolic_column]
                <
                df[diastolic_column]
            )

            |

            (
                df[systolic_column]
                > 300
            )

            |

            (
                df[diastolic_column]
                > 200
            )

            |

            (
                df[systolic_column]
                < 40
            )

            |

            (
                df[diastolic_column]
                < 20
            )
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

            "systolic_column":
                systolic_column,

            "diastolic_column":
                diastolic_column,

            "total_rows":
                len(df),

            "invalid_bp_count":
                invalid_count,

            "invalid_bp_percentage":
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
                "Blood pressure values appear valid."
            )

        else:

            recommendations.append(
                "Invalid blood pressure values detected. "
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