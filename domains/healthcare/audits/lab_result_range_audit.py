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


class LabResultRangeAudit(BaseAudit):

    audit_name = (
        "lab_result_range_audit"
    )

    category = "healthcare"

    LAB_RULES = {

        "glucose": {
            "min": 20,
            "max": 600
        },

        "hemoglobin": {
            "min": 3,
            "max": 25
        },

        "cholesterol": {
            "min": 50,
            "max": 500
        }
    }

    def run(
        self,
        dataset,
        context=None
    ):

        df = dataset.df

        invalid_columns = {}

        total_invalid_count = 0

        for column in df.columns:

            column_lower = (
                column.lower()
            )

            if (
                column_lower
                not in self.LAB_RULES
            ):

                continue

            min_value = (
                self.LAB_RULES[
                    column_lower
                ]["min"]
            )

            max_value = (
                self.LAB_RULES[
                    column_lower
                ]["max"]
            )

            invalid_mask = (

                (df[column] < min_value)

                |

                (df[column] > max_value)

            )

            invalid_count = int(
                invalid_mask.sum()
            )

            total_invalid_count += (
                invalid_count
            )

            invalid_columns[
                column
            ] = {

                "invalid_count":
                    invalid_count,

                "expected_range":
                    f"{min_value} - {max_value}"
            }

        if len(
            invalid_columns
        ) == 0:

            return AuditResult(

                audit_name=
                self.audit_name,

                category=
                self.category,

                passed=True,

                severity="INFO",

                findings={
                    "message":
                    "No supported lab result columns detected."
                },

                recommendations=[
                    "No lab result validation performed."
                ]
            )

        invalid_percentage = (
            calculate_percentage(
                total_invalid_count,
                len(df)
            )
        )

        findings = {

            "lab_columns_found":
                len(
                    invalid_columns
                ),

            "total_invalid_results":
                total_invalid_count,

            "invalid_percentage":
                invalid_percentage,

            "columns":
                invalid_columns
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
            total_invalid_count == 0
        )

        recommendations = []

        if (
            total_invalid_count == 0
        ):

            recommendations.append(
                "Lab result values appear valid."
            )

        else:

            recommendations.append(
                "Lab result values outside expected ranges detected."
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