from datawatcher.core.base_audit import (
    BaseAudit
)

from datawatcher.core.audit_result import (
    AuditResult
)

from datawatcher.utils.severity import (
    calculate_severity
)


class InterestRateAudit(BaseAudit):

    audit_name = (
        "interest_rate_audit"
    )

    category = "finance"

    INTEREST_RATE_KEYWORDS = [

        "interest",

        "interest_rate",

        "apr",

        "rate"
    ]

    def run(
        self,
        dataset,
        context=None
    ):

        df = dataset.df

        interest_columns = {}

        for column in df.columns:

            column_lower = (
                column.lower()
            )

            if not any(

                keyword
                in column_lower

                for keyword in
                self.INTEREST_RATE_KEYWORDS
            ):

                continue

            if not (
                df[column]
                .dtype.kind
                in "if"
            ):

                continue

            negative_count = int(
                (
                    df[column] < 0
                ).sum()
            )

            above_100_count = int(
                (
                    df[column] > 100
                ).sum()
            )

            invalid_count = (
                negative_count
                + above_100_count
            )

            interest_columns[
                column
            ] = {

                "negative_count":
                    negative_count,

                "above_100_count":
                    above_100_count,

                "invalid_count":
                    invalid_count
            }

        invalid_interest_columns = sum(

            1

            for details in
            interest_columns.values()

            if details[
                "invalid_count"
            ] > 0
        )

        findings = {

            "interest_rate_columns_found":
                len(
                    interest_columns
                ),

            "invalid_interest_columns":
                invalid_interest_columns,

            "interest_columns":
                interest_columns
        }

        severity = calculate_severity(

            value=
            invalid_interest_columns,

            low_threshold=1,

            medium_threshold=3
        )

        passed = (
            invalid_interest_columns
            == 0
        )

        recommendations = []

        if (
            len(
                interest_columns
            ) == 0
        ):

            recommendations.append(
                "No interest rate columns detected."
            )

        elif (
            invalid_interest_columns
            == 0
        ):

            recommendations.append(
                "Interest rate values appear valid."
            )

        else:

            recommendations.append(
                "Review interest rate columns for "
                "negative or unrealistic values."
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