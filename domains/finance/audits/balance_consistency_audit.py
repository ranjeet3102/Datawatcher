from datawatcher.core.base_audit import (
    BaseAudit
)

from datawatcher.core.audit_result import (
    AuditResult
)

from datawatcher.utils.severity import (
    calculate_severity
)

from datawatcher.utils.percentages import (
    calculate_percentage
)


class BalanceConsistencyAudit(BaseAudit):

    audit_name = (
        "balance_consistency_audit"
    )

    category = "finance"

    BALANCE_COLUMNS = {

        "opening_balance": [
            "opening_balance",
            "beginning_balance",
            "starting_balance"
        ],

        "credits": [
            "credits",
            "credit_amount",
            "deposits"
        ],

        "debits": [
            "debits",
            "debit_amount",
            "withdrawals"
        ],

        "closing_balance": [
            "closing_balance",
            "ending_balance",
            "final_balance"
        ]
    }

    def _find_column(
        self,
        df,
        aliases
    ):

        for column in df.columns:

            if (
                column.lower()
                in aliases
            ):
                return column

        return None

    def run(
        self,
        dataset,
        context=None
    ):

        df = dataset.df

        opening_col = self._find_column(
            df,
            self.BALANCE_COLUMNS[
                "opening_balance"
            ]
        )

        credits_col = self._find_column(
            df,
            self.BALANCE_COLUMNS[
                "credits"
            ]
        )

        debits_col = self._find_column(
            df,
            self.BALANCE_COLUMNS[
                "debits"
            ]
        )

        closing_col = self._find_column(
            df,
            self.BALANCE_COLUMNS[
                "closing_balance"
            ]
        )

        if not all([
            opening_col,
            credits_col,
            debits_col,
            closing_col
        ]):

            return AuditResult(

                audit_name=
                self.audit_name,

                category=
                self.category,

                passed=True,

                severity="INFO",

                findings={
                    "message":
                    "Required balance columns not found."
                },

                recommendations=[
                    "No balance validation performed."
                ]
            )

        expected_balance = (

            df[opening_col]
            +
            df[credits_col]
            -
            df[debits_col]
        )

        inconsistent_mask = (

            expected_balance
            !=
            df[closing_col]
        )

        inconsistent_rows = int(
            inconsistent_mask.sum()
        )

        inconsistency_percentage = (
            calculate_percentage(
                inconsistent_rows,
                len(df)
            )
        )

        findings = {

            "rows_checked":
                len(df),

            "inconsistent_rows":
                inconsistent_rows,

            "inconsistency_percentage":
                inconsistency_percentage,

            "detected_columns": {

                "opening_balance":
                    opening_col,

                "credits":
                    credits_col,

                "debits":
                    debits_col,

                "closing_balance":
                    closing_col
            }
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
            inconsistent_rows == 0
        )

        recommendations = []

        if (
            inconsistent_rows == 0
        ):

            recommendations.append(
                "Balance relationships appear consistent."
            )

        else:

            recommendations.append(
                "Balance inconsistencies detected. "
                "Review transaction calculations."
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