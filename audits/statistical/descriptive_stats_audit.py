from datawatcher.core.base_audit import (
    BaseAudit
)

from datawatcher.core.audit_result import (
    AuditResult
)

import pandas as pd


class DescriptiveStatsAudit(BaseAudit):

    audit_name = "descriptive_stats_audit"

    category = "statistical"

    def run(
        self,
        dataset,
        context=None
    ):

        df = dataset.df

        statistics = {}

        numeric_columns = df.select_dtypes(
            include=["number"]
        ).columns

        for column in numeric_columns:

            series = df[column].dropna()

            statistics[column] = {

                "count": int(
                    series.count()
                ),

                "mean": round(
                    float(series.mean()),
                    2
                ),

                "median": round(
                    float(series.median()),
                    2
                ),

                "std": round(
                    float(series.std()),
                    2
                ),

                "variance": round(
                    float(series.var()),
                    2
                ),

                "min": round(
                    float(series.min()),
                    2
                ),

                "q1": round(
                    float(
                        series.quantile(0.25)
                    ),
                    2
                ),

                "q3": round(
                    float(
                        series.quantile(0.75)
                    ),
                    2
                ),

                "max": round(
                    float(series.max()),
                    2
                )
            }

        findings = {

            "numeric_columns": int(
                len(numeric_columns)
            ),

            "statistics": statistics
        }

        return AuditResult(

            audit_name=self.audit_name,

            category=self.category,

            passed=True,

            severity="INFO",

            findings=findings,

            recommendations=[
                "Review numeric feature distributions before model training."
            ]
        )