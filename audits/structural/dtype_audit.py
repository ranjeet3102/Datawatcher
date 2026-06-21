import pandas as pd

from datawatcher.core.base_audit import (
    BaseAudit
)

from datawatcher.core.audit_result import (
    AuditResult
)


class DtypeAudit(BaseAudit):

    audit_name = "dtype_audit"

    category = "structural"

    SUPPORTED_DTYPES = {
        "int64",
        "float64",
        "bool",
        "boolean",
        "object",
        "str",      
        "string", 
        "datetime64[ns]"
    }

    def run(
        self,
        dataset,
        context=None
    ):

        df = dataset.df

        findings = {}

        unsupported_columns = []

        dtype_summary = {}

        for column in df.columns:

            dtype = str(df[column].dtype)

            dtype_summary[column] = dtype

            if dtype not in self.SUPPORTED_DTYPES:

                unsupported_columns.append(
                    column
                )

        findings["dtype_summary"] = (
            dtype_summary
        )

        findings["unsupported_columns"] = (
            unsupported_columns
        )

        findings["unsupported_count"] = (
            len(unsupported_columns)
        )

        passed = (
            len(unsupported_columns) == 0
        )

        if len(unsupported_columns) == 0:

            severity = "INFO"

        elif len(unsupported_columns) <= 2:

            severity = "MEDIUM"

        else:

            severity = "HIGH"

        recommendations = []

        if unsupported_columns:

            recommendations.append(
                "Review unsupported column dtypes."
            )

        return AuditResult(
            audit_name=self.audit_name,
            category=self.category,
            passed=passed,
            severity=severity,
            findings=findings,
            recommendations=recommendations
        )