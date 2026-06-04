from datawatcher.scoring.severity_weights import (
    SEVERITY_WEIGHTS
)

from datawatcher.scoring.audit_weights import (
    AUDIT_WEIGHTS
)


def calculate_total_penalty(
    audit_results
):

    total_penalty = 0

    severity_breakdown = {}

    for result in audit_results:

        severity = (
            result.severity.upper()
        )

        base_penalty = (
            SEVERITY_WEIGHTS.get(
                severity,
                0
            )
        )

        audit_weight = (
            AUDIT_WEIGHTS.get(
                result.audit_name,
                1.0
            )
        )

        weighted_penalty = (
            base_penalty
            * audit_weight
        )

        total_penalty += (
            weighted_penalty
        )

        severity_breakdown[
            result.audit_name
        ] = {

            "severity":
                severity,

            "base_penalty":
                base_penalty,

            "audit_weight":
                audit_weight,

            "weighted_penalty":
                round(
                    weighted_penalty,
                    2
                )
        }

    return {

        "total_penalty":
            round(
                total_penalty,
                2
            ),

        "severity_breakdown":
            severity_breakdown
    }