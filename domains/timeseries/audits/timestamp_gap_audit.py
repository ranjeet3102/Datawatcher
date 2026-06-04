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


class TimestampGapAudit(BaseAudit):

    audit_name = (
        "timestamp_gap_audit"
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
                    "No timestamp gap validation performed."
                ]
            )

        timestamps = (

            df[timestamp_column]
            .dropna()
            .sort_values()
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
                    "Insufficient timestamps for gap analysis."
                },

                recommendations=[
                    "Provide more timestamp records."
                ]
            )

        expected_range = (
            timestamps.max()
            -
            timestamps.min()
        ).days + 1

        actual_unique_dates = (
            timestamps.dt.normalize()
            .nunique()
        )

        missing_timestamps = (
            expected_range
            -
            actual_unique_dates
        )

        gap_percentage = (
            calculate_percentage(
                missing_timestamps,
                expected_range
            )
        )

        findings = {

            "timestamp_column":
                timestamp_column,

            "rows":
                len(df),

            "date_range_days":
                expected_range,

            "actual_dates":
                actual_unique_dates,

            "missing_timestamps":
                int(
                    missing_timestamps
                ),

            "gap_percentage":
                gap_percentage
        }

        severity = (
            calculate_severity(
                value=
                gap_percentage,

                low_threshold=1,

                medium_threshold=5
            )
        )

        passed = (
            missing_timestamps == 0
        )

        recommendations = []

        if (
            missing_timestamps == 0
        ):

            recommendations.append(
                "No timestamp gaps detected."
            )

        else:

            recommendations.append(
                "Timestamp gaps detected. "
                "Review missing periods before analysis."
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