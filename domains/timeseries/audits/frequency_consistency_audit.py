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


class FrequencyConsistencyAudit(BaseAudit):

    audit_name = (
        "frequency_consistency_audit"
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
                    "No frequency consistency validation performed."
                ]
            )

        timestamps = (

            df[timestamp_column]
            .dropna()
            .sort_values()
        )

        if len(timestamps) < 3:

            return AuditResult(

                audit_name=
                self.audit_name,

                category=
                self.category,

                passed=True,

                severity="INFO",

                findings={
                    "message":
                    "Insufficient timestamps for frequency analysis."
                },

                recommendations=[
                    "Provide more timestamp records."
                ]
            )

        intervals = (
            timestamps.diff()
            .dropna()
        )

        expected_interval = (
            intervals.mode()
            .iloc[0]
        )

        inconsistent_intervals = int(
            (
                intervals
                !=
                expected_interval
            ).sum()
        )

        inconsistency_percentage = (
            calculate_percentage(
                inconsistent_intervals,
                len(intervals)
            )
        )

        findings = {

            "timestamp_column":
                timestamp_column,

            "expected_frequency":
                str(
                    expected_interval
                ),

            "intervals_checked":
                len(
                    intervals
                ),

            "inconsistent_intervals":
                inconsistent_intervals,

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
            inconsistent_intervals == 0
        )

        recommendations = []

        if (
            inconsistent_intervals == 0
        ):

            recommendations.append(
                "Timestamp frequency is consistent."
            )

        else:

            recommendations.append(
                "Frequency inconsistencies detected. "
                "Review missing periods and data collection cadence."
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