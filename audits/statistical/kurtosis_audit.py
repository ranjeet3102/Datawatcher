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
    KURTOSIS_THRESHOLDS,
    KURTOTIC_FEATURE_COUNT_THRESHOLDS
)

from datawatcher.utils.recommendations import (
    kurtosis_recommendation
)


class KurtosisAudit(BaseAudit):

    audit_name = "kurtosis_audit"

    category = "statistical"

    def run(
        self,
        dataset,
        context=None
    ):

        df = dataset.df

        heavy_tailed_features = {}

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

            kurtosis = float(
                series.kurt()
            )

            if (
                abs(kurtosis)
                >= KURTOSIS_THRESHOLDS[
                    "high"
                ]
            ):

                heavy_tailed_features[
                    column
                ] = round(
                    kurtosis,
                    4
                )

        heavy_tail_count = len(
            heavy_tailed_features
        )

        findings = {

            "numeric_columns":
                len(numeric_columns),

            "heavy_tailed_feature_count":
                heavy_tail_count,

            "heavy_tailed_features":
                heavy_tailed_features
        }

        severity = calculate_severity(
            value=heavy_tail_count,
            low_threshold=
            KURTOTIC_FEATURE_COUNT_THRESHOLDS[
                "low"
            ],
            medium_threshold=
            KURTOTIC_FEATURE_COUNT_THRESHOLDS[
                "medium"
            ]
        )

        recommendations = [
            kurtosis_recommendation(
                heavy_tail_count
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