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
    LEAKAGE_THRESHOLDS,
    LEAKAGE_COUNT_THRESHOLDS
)

from datawatcher.utils.recommendations import (
    leakage_recommendation
)

import pandas as pd


class LeakageAudit(BaseAudit):

    audit_name = "leakage_audit"

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

        leakage_features = {}

        target_series = df[target]

        if (
            target_series.nunique()
            == 2
        ):

            target_numeric = (
                target_series.astype(int)
            )

        else:

            return AuditResult(
                audit_name=self.audit_name,
                category=self.category,
                passed=True,
                severity="INFO",
                findings={
                    "message":
                    "Leakage audit currently supports binary targets."
                },
                recommendations=[]
            )

        for column in df.columns:

            if column == target:
                continue

            risk_score = 0

            if (
                target.lower()
                in column.lower()
            ):
                risk_score += 1

            series = df[column]

            try:

                if (
                    series.equals(
                        target_series
                    )
                ):
                    risk_score += 2

            except Exception:
                pass

            try:

                if pd.api.types.is_numeric_dtype(
                    series
                ):

                    corr = abs(
                        float(
                            series.corr(
                                target_numeric
                            )
                        )
                    )

                    if (
                        corr >=
                        LEAKAGE_THRESHOLDS[
                            "correlation"
                        ]
                    ):

                        risk_score += 1

            except Exception:
                pass

            if risk_score >= 2:

                leakage_features[
                    column
                ] = {
                    "risk_score":
                        risk_score
                }

        leakage_count = len(
            leakage_features
        )

        findings = {

            "potential_leakage_count":
                leakage_count,

            "potential_leakage_features":
                leakage_features
        }

        severity = calculate_severity(
            value=leakage_count,
            low_threshold=
            LEAKAGE_COUNT_THRESHOLDS[
                "low"
            ],
            medium_threshold=
            LEAKAGE_COUNT_THRESHOLDS[
                "medium"
            ]
        )

        return AuditResult(
            audit_name=self.audit_name,
            category=self.category,
            passed=True,
            severity=severity,
            findings=findings,
            recommendations=[
                leakage_recommendation(
                    leakage_count
                )
            ]
        )