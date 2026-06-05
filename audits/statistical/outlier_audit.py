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
    OUTLIER_THRESHOLDS
)

from datawatcher.utils.recommendations import (
    outlier_pct_recommendation
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

        total_rows = len(df)

        outlier_features = {}

        total_outlier_rows = set()

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

            outlier_mask = (
                (df[column] < lower_bound)
                |
                (df[column] > upper_bound)
            )

            outlier_indices = (
                df.index[outlier_mask].tolist()
            )

            outlier_count = len(outlier_indices)

            if outlier_count > 0:

                outlier_pct = round(
                    (outlier_count / total_rows) * 100,
                    4
                )

                outlier_features[column] = {
                    "outlier_count": outlier_count,
                    "outlier_pct": outlier_pct,
                    "lower_bound": round(float(lower_bound), 4),
                    "upper_bound": round(float(upper_bound), 4)
                }

                # Track unique rows with any outlier (for overall %)
                total_outlier_rows.update(outlier_indices)

        total_outlier_row_count = len(total_outlier_rows)

        overall_outlier_pct = round(
            (total_outlier_row_count / total_rows) * 100,
            4
        ) if total_rows > 0 else 0.0

        findings = {

            "total_rows":
                total_rows,

            "numeric_columns_analyzed":
                len(numeric_columns),

            "outlier_feature_count":
                len(outlier_features),

            "total_outlier_rows":
                total_outlier_row_count,

            "overall_outlier_pct":
                overall_outlier_pct,

            "outlier_features":
                outlier_features
        }

        # Percentage-based severity — correct for large data
        severity = calculate_severity(
            value=overall_outlier_pct,
            low_threshold=OUTLIER_THRESHOLDS["low_pct"],
            medium_threshold=OUTLIER_THRESHOLDS["medium_pct"]
        )

        recommendations = [
            outlier_pct_recommendation(
                overall_outlier_pct
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