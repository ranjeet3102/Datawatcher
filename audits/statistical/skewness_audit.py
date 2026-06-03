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
    SKEWNESS_THRESHOLDS,
    SKEWED_FEATURE_COUNT_THRESHOLDS
)

from datawatcher.utils.recommendations import (
    skewness_recommendation
)


class SkewnessAudit(BaseAudit):

    audit_name = "skewness_audit"

    category = "statistical"

    def run(
        self,
        dataset,
        context=None
    ):

        df = dataset.df

        skewed_features = {}

        numeric_columns = (
            df.select_dtypes(
                include=["number"]
            ).columns
        )

        for column in numeric_columns:

            skewness = float(
                df[column]
                .dropna()
                .skew()
            )

            if (
                abs(skewness)
                >=
                SKEWNESS_THRESHOLDS["high"]
            ):

                skewed_features[
                    column
                ] = round(
                    skewness,
                    4
                )

        skewed_feature_count = len(
            skewed_features
        )

        findings = {

            "numeric_columns":
                len(numeric_columns),

            "skewed_feature_count":
                skewed_feature_count,

            "skewed_features":
                skewed_features
        }

        passed = (
            skewed_feature_count == 0
        )

        severity = calculate_severity(
            value=skewed_feature_count,
            low_threshold=
            SKEWED_FEATURE_COUNT_THRESHOLDS[
                "low"
            ],
            medium_threshold=
            SKEWED_FEATURE_COUNT_THRESHOLDS[
                "medium"
            ]
        )

        recommendations = [
            skewness_recommendation(
                skewed_feature_count
            )
        ]

        return AuditResult(
            audit_name=self.audit_name,
            category=self.category,
            passed=passed,
            severity=severity,
            findings=findings,
            recommendations=recommendations
        )