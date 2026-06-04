from datawatcher.core.base_audit import (
    BaseAudit
)

from datawatcher.core.audit_result import (
    AuditResult
)

from datawatcher.utils.severity import (
    calculate_severity
)


class NegativeValueAudit(BaseAudit):

    audit_name = "negative_value_audit"

    category = "finance"

    def run(
        self,
        dataset,
        context=None
    ):

        df = dataset.df

        negative_value_columns = {}

        numeric_columns = (
            df.select_dtypes(
                include=["number"]
            ).columns
        )

        for column in numeric_columns:

            negative_count = int(
                (df[column] < 0).sum()
            )

            if negative_count > 0:

                negative_percentage = round(
                    (
                        negative_count
                        / len(df)
                    ) * 100,
                    2
                )

                negative_value_columns[
                    column
                ] = {

                    "negative_count":
                        negative_count,

                    "negative_percentage":
                        negative_percentage
                }

        columns_with_negative_values = len(
            negative_value_columns
        )

        findings = {

            "numeric_columns":
                len(
                    numeric_columns
                ),

            "columns_with_negative_values":
                columns_with_negative_values,

            "negative_value_columns":
                negative_value_columns
        }

        severity = calculate_severity(
            value=
            columns_with_negative_values,

            low_threshold=1,

            medium_threshold=3
        )

        recommendations = []

        if (
            columns_with_negative_values
            == 0
        ):

            recommendations.append(
                "No negative values detected."
            )

        elif (
            columns_with_negative_values
            <= 2
        ):

            recommendations.append(
                "Review columns containing negative values."
            )

        else:

            recommendations.append(
                "Multiple columns contain negative values. "
                "Validate business rules and data quality."
            )

        return AuditResult(
            audit_name=self.audit_name,
            category=self.category,

            # Observational audit
            passed=True,

            severity=severity,

            findings=findings,

            recommendations=
            recommendations
        )