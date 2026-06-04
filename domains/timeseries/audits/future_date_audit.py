from datetime import datetime

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


class FutureDateAudit(BaseAudit):

    audit_name = (
        "future_date_audit"
    )

    category = "timeseries"

    def run(
        self,
        dataset,
        context=None
    ):

        df = dataset.df

        timestamp_column = None

        for column, semantic_type in (
            dataset.semantic_types.items()
        ):

            if semantic_type in [
                "datetime",
                "timestamp",
                "date"
            ]:

                timestamp_column = column

                break

        if timestamp_column is None:

            return AuditResult(

                audit_name=
                self.audit_name,

                category=
                self.category,

                passed=True,

                severity="INFO",

                findings={
                    "message":
                    "No timestamp column detected."
                },

                recommendations=[
                    "No future date validation performed."
                ]
            )

        current_timestamp = (
            datetime.now()
        )

        future_dates = (

            df[timestamp_column]
            >
            current_timestamp

        )

        future_date_count = int(
            future_dates.sum()
        )

        future_date_percentage = (
            calculate_percentage(
                future_date_count,
                len(df)
            )
        )

        findings = {

            "timestamp_column":
                timestamp_column,

            "total_rows":
                len(df),

            "future_date_count":
                future_date_count,

            "future_date_percentage":
                future_date_percentage
        }

        severity = (
            calculate_severity(
                value=
                future_date_percentage,

                low_threshold=1,

                medium_threshold=5
            )
        )

        passed = (
            future_date_count == 0
        )

        recommendations = []

        if (
            future_date_count == 0
        ):

            recommendations.append(
                "No future dates detected."
            )

        else:

            recommendations.append(
                "Future dates detected. "
                "Review timestamp generation and ingestion logic."
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