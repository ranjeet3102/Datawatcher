from datawatcher.core.base_audit import (
    BaseAudit
)

from datawatcher.core.audit_result import (
    AuditResult
)

from datawatcher.utils.severity import (
    calculate_severity
)

from datawatcher.utils.thresholds import (
    OUTLIER_COUNT_THRESHOLDS
)

from datawatcher.utils.recommendations import (
    outlier_recommendation
)


class OutlierAudit(BaseAudit):

    audit_name = "outlier_audit"

    category = "statistical"

    def run(
        self,
        dataset,
        context=None
    ):

        df = dataset.df

        outlier_features = {}

        total_outliers = 0

        numeric_columns = (
            df.select_dtypes(
                include=["number"]
            ).columns
        )

        for column in numeric_columns:

            series = df[column].dropna()

            # Skip binary features
            if (
                series.nunique()
                <= 2
            ):
                continue

            q1 = series.quantile(0.25)

            q3 = series.quantile(0.75)

            iqr = q3 - q1

            lower_bound = (
                q1 - (1.5 * iqr)
            )

            upper_bound = (
                q3 + (1.5 * iqr)
            )

            outlier_count = int(
                (
                    (series < lower_bound)
                    |
                    (series > upper_bound)
                ).sum()
            )

            if outlier_count > 0:

                outlier_features[
                    column
                ] = outlier_count

                total_outliers += (
                    outlier_count
                )

        findings = {

            "numeric_columns":
                len(numeric_columns),

            "outlier_feature_count":
                len(outlier_features),

            "total_outliers":
                total_outliers,

            "outlier_features":
                outlier_features
        }

        severity = calculate_severity(
            value=total_outliers,
            low_threshold=
            OUTLIER_COUNT_THRESHOLDS[
                "low"
            ],
            medium_threshold=
            OUTLIER_COUNT_THRESHOLDS[
                "medium"
            ]
        )

        recommendations = [
            outlier_recommendation(
                total_outliers
            )
        ]

        return AuditResult(
            audit_name=self.audit_name,
            category=self.category,
            passed=True,
            severity=severity,
            findings=findings,
            recommendations=recommendations
        )