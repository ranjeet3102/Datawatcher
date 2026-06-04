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


class DuplicateTimestampAudit(BaseAudit):

    audit_name = (
        "duplicate_timestamp_audit"
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
                    "No duplicate timestamp validation performed."
                ]
            )

        duplicate_count = int(

            df[timestamp_column]
            .duplicated()
            .sum()

        )

        duplicate_percentage = (
            calculate_percentage(
                duplicate_count,
                len(df)
            )
        )

        findings = {

            "timestamp_column":
                timestamp_column,

            "total_rows":
                len(df),

            "duplicate_timestamps":
                duplicate_count,

            "duplicate_percentage":
                duplicate_percentage
        }

        severity = (
            calculate_severity(
                value=
                duplicate_percentage,

                low_threshold=1,

                medium_threshold=5
            )
        )

        passed = (
            duplicate_count == 0
        )

        recommendations = []

        if (
            duplicate_count == 0
        ):

            recommendations.append(
                "No duplicate timestamps detected."
            )

        else:

            recommendations.append(
                "Duplicate timestamps detected. "
                "Review aggregation and ingestion logic."
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