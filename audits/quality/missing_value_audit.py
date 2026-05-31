from datawatcher.core.base_audit import BaseAudit
from datawatcher.core.audit_result import AuditResult

from datawatcher.utils.percentages import calculate_percentage
from datawatcher.utils.severity import calculate_severity
from datawatcher.utils.thresholds import (
    MISSING_VALUE_THRESHOLDS
)
from datawatcher.utils.recommendations import (
    missing_value_recommendation
)


class MissingValueAudit(BaseAudit):

    audit_name = "missing_value_audit"

    category = "quality"

    def run(
        self,
        dataset,
        context=None
    ):

        df = dataset.df

        total_cells = df.shape[0] * df.shape[1]

        total_missing = df.isna().sum().sum()

        overall_missing_percentage = calculate_percentage(
            total_missing,
            total_cells
        )

        column_missing_stats = {}

        for column in df.columns:

            missing_count = df[column].isna().sum()

            missing_percentage = calculate_percentage(
                missing_count,
                len(df)
            )

            if missing_count > 0:

                column_missing_stats[column] = {
                    "missing_count": int(missing_count),
                    "missing_percentage": missing_percentage
                }

        severity = calculate_severity(
            value=overall_missing_percentage,
            low_threshold=MISSING_VALUE_THRESHOLDS["low"],
            medium_threshold=MISSING_VALUE_THRESHOLDS["medium"]
        )

        passed = overall_missing_percentage < (
            MISSING_VALUE_THRESHOLDS["medium"]
        )

        findings = {
            "total_missing_cells": int(total_missing),
            "overall_missing_percentage": (
                overall_missing_percentage
            ),
            "columns_with_missing": (
                len(column_missing_stats)
            ),
            "column_missing_stats": (
                column_missing_stats
            )
        }

        recommendations = [
            missing_value_recommendation(
                overall_missing_percentage
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