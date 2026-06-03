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
    CATEGORY_IMBALANCE_THRESHOLDS,
    CATEGORY_IMBALANCE_COUNT_THRESHOLDS
)

from datawatcher.utils.recommendations import (
    category_imbalance_recommendation
)


class CategoryImbalanceAudit(BaseAudit):

    audit_name = (
        "category_imbalance_audit"
    )

    category = "categorical"

    def run(
        self,
        dataset,
        context=None
    ):

        df = dataset.df

        imbalanced_features = {}

        for column, semantic_type in (
            dataset.semantic_types.items()
        ):

            if (
                semantic_type
                != "categorical"
            ):
                continue

            distribution = (
                df[column]
                .value_counts(
                    normalize=True,
                    dropna=False
                ) * 100
            )

            if len(distribution) == 0:
                continue

            dominant_category = (
                distribution.idxmax()
            )

            dominance_percentage = (
                float(
                    distribution.max()
                )
            )

            if (
                dominance_percentage
                >=
                CATEGORY_IMBALANCE_THRESHOLDS[
                    "dominance_ratio"
                ]
            ):

                imbalanced_features[
                    column
                ] = {

                    "dominant_category":
                        str(
                            dominant_category
                        ),

                    "percentage":
                        round(
                            dominance_percentage,
                            2
                        )
                }

        imbalance_count = len(
            imbalanced_features
        )

        findings = {

            "imbalanced_feature_count":
                imbalance_count,

            "imbalanced_features":
                imbalanced_features
        }

        severity = calculate_severity(
            value=imbalance_count,
            low_threshold=
            CATEGORY_IMBALANCE_COUNT_THRESHOLDS[
                "low"
            ],
            medium_threshold=
            CATEGORY_IMBALANCE_COUNT_THRESHOLDS[
                "medium"
            ]
        )

        recommendations = [
            category_imbalance_recommendation(
                imbalance_count
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