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
    NEAR_CONSTANT_THRESHOLDS,
    NEAR_CONSTANT_COUNT_THRESHOLDS
)

from datawatcher.utils.recommendations import (
    near_constant_recommendation
)


class NearConstantAudit(BaseAudit):

    audit_name = "near_constant_audit"

    category = "quality"

    def run(
        self,
        dataset,
        context=None
    ):

        df = dataset.df

        near_constant_features = {}

        for column in df.columns:

            value_distribution = (
                df[column]
                .value_counts(
                    normalize=True,
                    dropna=False
                )
            )

            if len(value_distribution) == 0:

                continue

            dominance_ratio = float(
                value_distribution.iloc[0]
            )

            if (
                dominance_ratio
                >= NEAR_CONSTANT_THRESHOLDS[
                    "dominance_ratio"
                ]
            ):

                near_constant_features[
                    column
                ] = round(
                    dominance_ratio,
                    4
                )

        near_constant_count = len(
            near_constant_features
        )

        findings = {
            "near_constant_feature_count":
                near_constant_count,
            "near_constant_features":
                near_constant_features
        }

        passed = (
            near_constant_count == 0
        )

        severity = calculate_severity(
            value=near_constant_count,
            low_threshold=
            NEAR_CONSTANT_COUNT_THRESHOLDS[
                "low"
            ],
            medium_threshold=
            NEAR_CONSTANT_COUNT_THRESHOLDS[
                "medium"
            ]
        )

        recommendations = [
            near_constant_recommendation(
                near_constant_count
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