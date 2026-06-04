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


class MissingDiagnosisAudit(BaseAudit):

    audit_name = (
        "missing_diagnosis_audit"
    )

    category = "healthcare"

    DIAGNOSIS_KEYWORDS = [

        "diagnosis",

        "diagnosis_code",

        "diagnosis_name",

        "condition",

        "disease"
    ]

    def run(
        self,
        dataset,
        context=None
    ):

        df = dataset.df

        diagnosis_column = None

        for column in df.columns:

            if (
                column.lower()
                in self.DIAGNOSIS_KEYWORDS
            ):

                diagnosis_column = column

                break

        if diagnosis_column is None:

            return AuditResult(

                audit_name=
                self.audit_name,

                category=
                self.category,

                passed=True,

                severity="INFO",

                findings={
                    "message":
                    "No diagnosis column detected."
                },

                recommendations=[
                    "No diagnosis validation performed."
                ]
            )

        diagnosis_series = (
            df[diagnosis_column]
            .astype(str)
            .str.strip()
        )

        missing_mask = (

            diagnosis_series.isna()

            |

            (diagnosis_series == "")

            |

            (
                diagnosis_series
                .str.lower()
                .isin(
                    [
                        "unknown",
                        "na",
                        "n/a",
                        "null",
                        "none"
                    ]
                )
            )
        )

        missing_count = int(
            missing_mask.sum()
        )

        missing_percentage = (
            calculate_percentage(
                missing_count,
                len(df)
            )
        )

        findings = {

            "diagnosis_column":
                diagnosis_column,

            "total_rows":
                len(df),

            "missing_diagnosis_count":
                missing_count,

            "missing_diagnosis_percentage":
                missing_percentage
        }

        severity = (
            calculate_severity(
                value=
                missing_percentage,

                low_threshold=1,

                medium_threshold=5
            )
        )

        passed = (
            missing_count == 0
        )

        recommendations = []

        if (
            missing_count == 0
        ):

            recommendations.append(
                "Diagnosis information is complete."
            )

        else:

            recommendations.append(
                "Missing diagnosis values detected. "
                "Review patient records."
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