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
    VARIANCE_THRESHOLDS,
    LOW_VARIANCE_COUNT_THRESHOLDS
)

from datawatcher.utils.recommendations import (
    variance_recommendation
)

import pandas as pd


class VarianceAudit(BaseAudit):

    audit_name = "variance_audit"

    category = "statistical"

    def run(
        self,
        dataset,
        context=None
    ):

        df = dataset.df

        low_variance_features = {}

        numeric_columns = df.select_dtypes(
            include=["number"]
        ).columns

        for column in numeric_columns:

            variance = float(
                df[column]
                .dropna()
                .var()
            )

            if (
                variance <
                VARIANCE_THRESHOLDS[
                    "low_variance"
                ]
            ):

                low_variance_features[
                    column
                ] = round(
                    variance,
                    6
                )

        low_variance_count = len(
            low_variance_features
        )

        findings = {

            "numeric_columns":
                len(numeric_columns),

            "low_variance_feature_count":
                low_variance_count,

            "low_variance_features":
                low_variance_features
        }

        passed = (
            low_variance_count == 0
        )

        severity = calculate_severity(
            value=low_variance_count,
            low_threshold=
            LOW_VARIANCE_COUNT_THRESHOLDS[
                "low"
            ],
            medium_threshold=
            LOW_VARIANCE_COUNT_THRESHOLDS[
                "medium"
            ]
        )

        recommendations = [
            variance_recommendation(
                low_variance_count
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