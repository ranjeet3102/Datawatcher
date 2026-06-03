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
    IDENTIFIER_RISK_THRESHOLDS,
    IDENTIFIER_RISK_COUNT_THRESHOLDS
)

from datawatcher.utils.recommendations import (
    identifier_risk_recommendation
)


IDENTIFIER_KEYWORDS = [
    "id",
    "userid",
    "customerid",
    "accountid",
    "transactionid",
    "orderid",
    "email",
    "phone"
]


class IdentifierRiskAudit(BaseAudit):

    audit_name = (
        "identifier_risk_audit"
    )

    category = "ml"

    def run(
        self,
        dataset,
        context=None
    ):

        df = dataset.df

        row_count = len(df)

        risk_features = {}

        for column, semantic_type in (
            dataset.semantic_types.items()
        ):

            risk_score = 0

            column_lower = (
                column.lower()
            )

            if (
                semantic_type
                == "identifier"
            ):

                risk_score += 1

            unique_values = int(
                df[column].nunique(
                    dropna=False
                )
            )

            cardinality_ratio = (
                unique_values / row_count
            )

            if (
                cardinality_ratio
                >=
                IDENTIFIER_RISK_THRESHOLDS[
                    "high_cardinality_ratio"
                ]
            ):

                risk_score += 1

            if any(
                keyword in column_lower
                for keyword in
                IDENTIFIER_KEYWORDS
            ):

                risk_score += 1

            if risk_score >= 2:

                risk_features[
                    column
                ] = {

                    "risk_score":
                        risk_score,

                    "cardinality_ratio":
                        round(
                            cardinality_ratio,
                            4
                        )
                }

        risk_count = len(
            risk_features
        )

        findings = {

            "identifier_risk_count":
                risk_count,

            "identifier_risk_features":
                risk_features
        }

        severity = calculate_severity(
            value=risk_count,
            low_threshold=
            IDENTIFIER_RISK_COUNT_THRESHOLDS[
                "low"
            ],
            medium_threshold=
            IDENTIFIER_RISK_COUNT_THRESHOLDS[
                "medium"
            ]
        )

        recommendations = [
            identifier_risk_recommendation(
                risk_count
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