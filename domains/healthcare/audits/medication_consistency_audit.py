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


class MedicationConsistencyAudit(BaseAudit):

    audit_name = (
        "medication_consistency_audit"
    )

    category = "healthcare"

    DIAGNOSIS_KEYWORDS = [

        "diagnosis",

        "diagnosis_code",

        "condition",

        "disease"
    ]

    MEDICATION_KEYWORDS = [

        "medication",

        "drug",

        "prescription",

        "medicine"
    ]

    def run(
        self,
        dataset,
        context=None
    ):

        df = dataset.df

        diagnosis_column = None
        medication_column = None

        for column in df.columns:

            column_lower = (
                column.lower()
            )

            if (
                column_lower
                in self.DIAGNOSIS_KEYWORDS
            ):

                diagnosis_column = column

            if (
                column_lower
                in self.MEDICATION_KEYWORDS
            ):

                medication_column = column

        if (
            diagnosis_column is None
            or
            medication_column is None
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
                    "Diagnosis or medication column not detected."
                },

                recommendations=[
                    "No medication consistency validation performed."
                ]
            )

        diagnosis_present = (

            ~df[diagnosis_column]
            .isna()

        )

        medication_missing = (

            df[medication_column]
            .isna()

            |

            (
                df[medication_column]
                .astype(str)
                .str.strip()
                .str.lower()
                .isin(
                    [
                        "",
                        "unknown",
                        "na",
                        "n/a",
                        "null",
                        "none",
                        "nan"
                    ]
                )
            )
        )

        inconsistent_mask = (

            diagnosis_present

            &

            medication_missing

        )

        inconsistent_count = int(
            inconsistent_mask.sum()
        )

        inconsistency_percentage = (
            calculate_percentage(
                inconsistent_count,
                len(df)
            )
        )

        findings = {

            "diagnosis_column":
                diagnosis_column,

            "medication_column":
                medication_column,

            "total_rows":
                len(df),

            "inconsistent_records":
                inconsistent_count,

            "inconsistency_percentage":
                inconsistency_percentage
        }

        severity = (
            calculate_severity(
                value=
                inconsistency_percentage,

                low_threshold=1,

                medium_threshold=5
            )
        )

        passed = (
            inconsistent_count == 0
        )

        recommendations = []

        if (
            inconsistent_count == 0
        ):

            recommendations.append(
                "Medication records appear consistent."
            )

        else:

            recommendations.append(
                "Diagnosis records without medication detected. "
                "Review treatment documentation."
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