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


class TimeOrderAudit(BaseAudit):

    audit_name = (
        "time_order_audit"
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
                    "No timestamp ordering validation performed."
                ]
            )

        timestamps = (
            df[timestamp_column]
            .dropna()
        )

        if len(timestamps) < 2:

            return AuditResult(

                audit_name=
                self.audit_name,

                category=
                self.category,

                passed=True,

                severity="INFO",

                findings={
                    "message":
                    "Insufficient timestamps for ordering analysis."
                },

                recommendations=[
                    "Provide more timestamp records."
                ]
            )

        out_of_order_count = 0

        for i in range(
            1,
            len(timestamps)
        ):

            if (
                timestamps.iloc[i]
                <
                timestamps.iloc[i - 1]
            ):

                out_of_order_count += 1

        out_of_order_percentage = (
            calculate_percentage(
                out_of_order_count,
                len(timestamps)
            )
        )

        findings = {

            "timestamp_column":
                timestamp_column,

            "total_rows":
                len(df),

            "out_of_order_rows":
                out_of_order_count,

            "out_of_order_percentage":
                out_of_order_percentage
        }

        severity = (
            calculate_severity(
                value=
                out_of_order_percentage,

                low_threshold=1,

                medium_threshold=5
            )
        )

        passed = (
            out_of_order_count == 0
        )

        recommendations = []

        if (
            out_of_order_count == 0
        ):

            recommendations.append(
                "Timestamp ordering is correct."
            )

        else:

            recommendations.append(
                "Timestamp ordering issues detected. "
                "Sort data before downstream analysis."
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