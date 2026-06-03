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
    CONSTANT_FEATURE_THRESHOLDS
)

from datawatcher.utils.recommendations import (
    constant_feature_recommendation
)


class ConstantFeatureAudit(BaseAudit):

    audit_name = "constant_feature_audit"

    category = "quality"

    def run(
        self,
        dataset,
        context=None
    ):

        df = dataset.df

        constant_features = []

        for column in df.columns:

            unique_count = (
                df[column]
                .nunique(dropna=False)
            )

            if unique_count <= 1:

                constant_features.append(
                    column
                )

        constant_count = len(
            constant_features
        )

        findings = {
            "constant_feature_count": (
                constant_count
            ),
            "constant_features": (
                constant_features
            )
        }

        passed = (
            constant_count == 0
        )

        severity = calculate_severity(
            value=constant_count,
            low_threshold=CONSTANT_FEATURE_THRESHOLDS["low"],
            medium_threshold=CONSTANT_FEATURE_THRESHOLDS["medium"]
        )

        recommendations = [
            constant_feature_recommendation(
                constant_count
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