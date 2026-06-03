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
    RARE_CATEGORY_THRESHOLDS,
    RARE_CATEGORY_COUNT_THRESHOLDS
)

from datawatcher.utils.recommendations import (
    rare_category_recommendation
)


class RareCategoryAudit(BaseAudit):

    audit_name = "rare_category_audit"

    category = "categorical"

    def run(
        self,
        dataset,
        context=None
    ):

        df = dataset.df

        rare_categories = {}

        total_rare_categories = 0

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

            column_rare = {}

            for category, percentage in (
                distribution.items()
            ):

                if (
                    percentage
                    <
                    RARE_CATEGORY_THRESHOLDS[
                        "rare_percentage"
                    ]
                ):

                    column_rare[
                        str(category)
                    ] = round(
                        float(
                            percentage
                        ),
                        2
                    )

            if column_rare:

                rare_categories[
                    column
                ] = column_rare

                total_rare_categories += (
                    len(column_rare)
                )

        findings = {

            "rare_category_columns":
                len(rare_categories),

            "rare_categories":
                rare_categories,

            "total_rare_categories":
                total_rare_categories
        }

        severity = calculate_severity(
            value=total_rare_categories,
            low_threshold=
            RARE_CATEGORY_COUNT_THRESHOLDS[
                "low"
            ],
            medium_threshold=
            RARE_CATEGORY_COUNT_THRESHOLDS[
                "medium"
            ]
        )

        recommendations = [
            rare_category_recommendation(
                total_rare_categories
            )
        ]

        return AuditResult(
            audit_name=self.audit_name,
            category=self.category,
            passed=(
                total_rare_categories == 0
            ),
            severity=severity,
            findings=findings,
            recommendations=recommendations
        )