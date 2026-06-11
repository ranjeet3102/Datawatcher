from datawatcher.scoring.severity_scorer import (
    calculate_total_penalty
)


MAX_SCORE = 100

def readiness_grade(
    score: int
) -> str:

    if score >= 90:
        return "EXCELLENT"

    if score >= 75:
        return "GOOD"

    if score >= 60:
        return "FAIR"

    return "POOR"


def calculate_ml_readiness_score(
    audit_results
):
    

    penalty_result = (
        calculate_total_penalty(
            audit_results
        )
    )

    total_penalty = (
        penalty_result[
            "total_penalty"
        ]
    )

    score = (
        MAX_SCORE
        - total_penalty
    )

    score = max(
        0,
        score
    )

    return {

    "ml_readiness_score":
        score,

    "grade":
        readiness_grade(score),

    "total_penalty":
        total_penalty,

    "severity_breakdown":
        penalty_result[
            "severity_breakdown"
        ]
}