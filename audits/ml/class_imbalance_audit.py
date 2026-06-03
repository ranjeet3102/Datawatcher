from datawatcher.core.base_audit import (
    BaseAudit
)

from datawatcher.core.audit_result import (
    AuditResult
)

from datawatcher.utils.thresholds import (
    CLASS_IMBALANCE_THRESHOLDS
)

from datawatcher.utils.recommendations import (
    class_imbalance_recommendation
)


class ClassImbalanceAudit(BaseAudit):

    audit_name = (
        "class_imbalance_audit"
    )

    category = "ml"

    def run(
        self,
        dataset,
        context=None
    ):

        df = dataset.df

        target = None

        if context:

            target = context.get(
                "target"
            )

        if (
            not target
            or target not in df.columns
        ):

            return AuditResult(
                audit_name=self.audit_name,
                category=self.category,
                passed=False,
                severity="HIGH",
                findings={
                    "error":
                    "Valid target required."
                },
                recommendations=[
                    "Provide a valid target."
                ]
            )

        distribution = (
            df[target]
            .value_counts(
                normalize=True,
                dropna=False
            ) * 100
        )

        class_distribution = {}

        for cls, pct in (
            distribution.items()
        ):

            class_distribution[
                str(cls)
            ] = round(
                float(pct),
                2
            )

        dominant_class = (
            distribution.idxmax()
        )

        dominant_pct = float(
            distribution.max()
        )

        imbalanced = (
            dominant_pct
            >=
            CLASS_IMBALANCE_THRESHOLDS[
                "dominance_ratio"
            ]
        )

        severity = (
            "LOW"
            if not imbalanced
            else "HIGH"
        )

        findings = {

            "target_column":
                target,

            "class_distribution":
                class_distribution,

            "dominant_class":
                str(
                    dominant_class
                ),

            "dominant_class_percentage":
                round(
                    dominant_pct,
                    2
                ),

            "imbalanced":
                imbalanced
        }

        return AuditResult(
            audit_name=self.audit_name,
            category=self.category,
            passed=True,
            severity=severity,
            findings=findings,
            recommendations=[
                class_imbalance_recommendation(
                    imbalanced
                )
            ]
        )