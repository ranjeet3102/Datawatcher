from datawatcher.core.base_audit import (
    BaseAudit
)

from datawatcher.core.audit_result import (
    AuditResult
)


class CategoryFrequencyAudit(BaseAudit):

    audit_name = (
        "category_frequency_audit"
    )

    category = "categorical"

    def run(
        self,
        dataset,
        context=None
    ):

        df = dataset.df

        frequencies = {}

        for column, semantic_type in (
            dataset.semantic_types.items()
        ):

            if (
                semantic_type
                != "categorical"
            ):
                continue

            counts = (
                df[column]
                .value_counts(
                    dropna=False
                )
            )

            percentages = (
                df[column]
                .value_counts(
                    normalize=True,
                    dropna=False
                ) * 100
            )

            frequencies[column] = {}

            for category in counts.index:

                frequencies[column][
                    str(category)
                ] = {

                    "count": int(
                        counts[category]
                    ),

                    "percentage": round(
                        float(
                            percentages[
                                category
                            ]
                        ),
                        2
                    )
                }

        findings = {

            "categorical_columns":
                len(frequencies),

            "category_frequencies":
                frequencies
        }

        return AuditResult(
            audit_name=self.audit_name,
            category=self.category,
            passed=True,
            severity="INFO",
            findings=findings,
            recommendations=[
                (
                    "Review category distributions "
                    "before encoding."
                )
            ]
        )