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
    CARDINALITY_THRESHOLDS,
    HIGH_CARDINALITY_COUNT_THRESHOLDS
)

from datawatcher.utils.recommendations import (
    cardinality_recommendation
)


class CardinalityAudit(BaseAudit):

    audit_name = "cardinality_audit"

    category = "ml"

    def run(
        self,
        dataset,
        context=None
    ):

        df = dataset.df

        row_count = len(df)

        high_cardinality_features = {}

        for column, semantic_type in (
            dataset.semantic_types.items()
        ):

            if semantic_type not in [
                "categorical",
                "text",
                "identifier"
            ]:
                continue

            unique_values = int(
                df[column].nunique(
                    dropna=False
                )
            )

            cardinality_ratio = (
                unique_values / row_count
            )

            if (
                cardinality_ratio
                >=
                CARDINALITY_THRESHOLDS[
                    "high_cardinality_ratio"
                ]
            ):

                high_cardinality_features[
                    column
                ] = {

                    "unique_values":
                        unique_values,

                    "cardinality_ratio":
                        round(
                            cardinality_ratio,
                            4
                        )
                }

        feature_count = len(
            high_cardinality_features
        )

        findings = {

            "high_cardinality_feature_count":
                feature_count,

            "high_cardinality_features":
                high_cardinality_features
        }

        severity = calculate_severity(
            value=feature_count,
            low_threshold=
            HIGH_CARDINALITY_COUNT_THRESHOLDS[
                "low"
            ],
            medium_threshold=
            HIGH_CARDINALITY_COUNT_THRESHOLDS[
                "medium"
            ]
        )

        recommendations = [
            cardinality_recommendation(
                feature_count
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