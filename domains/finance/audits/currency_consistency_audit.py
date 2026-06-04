from datawatcher.core.base_audit import (
    BaseAudit
)

from datawatcher.core.audit_result import (
    AuditResult
)

from datawatcher.utils.severity import (
    calculate_severity
)


class CurrencyConsistencyAudit(BaseAudit):

    audit_name = (
        "currency_consistency_audit"
    )

    category = "finance"

    CURRENCY_KEYWORDS = [

        "currency",

        "currency_code",

        "curr",

        "payment_currency"
    ]

    def run(
        self,
        dataset,
        context=None
    ):

        df = dataset.df

        currency_columns = {}

        for column in df.columns:

            column_lower = (
                column.lower()
            )

            if not any(

                keyword
                in column_lower

                for keyword in
                self.CURRENCY_KEYWORDS
            ):

                continue

            values = (
                df[column]
                .dropna()
                .astype(str)
            )

            unique_values = sorted(
                values.unique().tolist()
            )

            unique_count = len(
                unique_values
            )

            missing_count = int(
                df[column]
                .isna()
                .sum()
            )

            currency_columns[
                column
            ] = {

                "unique_values":
                    unique_values,

                "unique_count":
                    unique_count,

                "missing_count":
                    missing_count
            }

        currency_column_count = len(
            currency_columns
        )

        inconsistent_column_count = 0

        for details in (
            currency_columns.values()
        ):

            if (
                details[
                    "unique_count"
                ] > 1
            ):

                inconsistent_column_count += 1

        findings = {

            "currency_columns_found":
                currency_column_count,

            "inconsistent_columns":
                inconsistent_column_count,

            "currency_columns":
                currency_columns
        }

        severity = calculate_severity(
            value=
            inconsistent_column_count,

            low_threshold=1,

            medium_threshold=3
        )

        passed = (
            inconsistent_column_count
            == 0
        )

        recommendations = []

        if (
            currency_column_count
            == 0
        ):

            recommendations.append(
                "No currency columns detected."
            )

        elif (
            inconsistent_column_count
            == 0
        ):

            recommendations.append(
                "Currency values appear consistent."
            )

        elif (
            inconsistent_column_count
            <= 2
        ):

            recommendations.append(
                "Review currency formatting and standardize currency values."
            )

        else:

            recommendations.append(
                "Multiple currency consistency issues detected. "
                "Consider applying currency normalization rules."
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