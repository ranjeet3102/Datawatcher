from datawatcher.core.base_audit import (
    BaseAudit
)

from datawatcher.core.audit_result import (
    AuditResult
)

from datawatcher.utils.recommendations import (
    target_validation_recommendation
)

import pandas as pd


class TargetValidationAudit(BaseAudit):

    audit_name = (
        "target_validation_audit"
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

        if not target:

            return AuditResult(
                audit_name=self.audit_name,
                category=self.category,
                passed=False,
                severity="HIGH",
                findings={
                    "error":
                    "No target specified."
                },
                recommendations=[
                    "Provide a target column."
                ]
            )

        if target not in df.columns:

            return AuditResult(
                audit_name=self.audit_name,
                category=self.category,
                passed=False,
                severity="HIGH",
                findings={
                    "error":
                    f"Target '{target}' not found."
                },
                recommendations=[
                    "Verify target column name."
                ]
            )

        non_null_count = int(
            df[target]
            .notna()
            .sum()
        )

        unique_classes = int(
            df[target]
            .nunique(
                dropna=True
            )
        )

        passed = True

        severity = "INFO"

        if non_null_count == 0:

            passed = False

            severity = "HIGH"

        elif unique_classes < 2:

            passed = False

            severity = "HIGH"

        if pd.api.types.is_numeric_dtype(
            df[target]
        ):

            if unique_classes > 20:

                problem_type = (
                    "regression"
                )

            else:

                problem_type = (
                    "classification"
                )

        else:

            if unique_classes == 2:

                problem_type = (
                    "binary_classification"
                )

            else:

                problem_type = (
                    "multiclass_classification"
                )

        findings = {

            "target_column":
                target,

            "exists":
                True,

            "non_null_count":
                non_null_count,

            "unique_classes":
                unique_classes,

            "problem_type":
                problem_type
        }

        return AuditResult(
            audit_name=self.audit_name,
            category=self.category,
            passed=passed,
            severity=severity,
            findings=findings,
            recommendations=[
                target_validation_recommendation(
                    passed
                )
            ]
        )