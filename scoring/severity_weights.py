# ============================================================
# Severity Penalty Weights
#
# Applied as: penalty = base_weight × audit_weight
# Total penalty subtracted from 100 to yield ML readiness score.
#
# Weights increased for better score separation at scale:
# even LOW issues compound across many columns in large datasets.
# ============================================================
SEVERITY_WEIGHTS = {

    "INFO": 0,      # Observational — no penalty

    "LOW": 3,       # was 2 — minor issues still matter at scale

    "MEDIUM": 7,    # was 5 — clearer separation from LOW

    "HIGH": 15,     # was 10 — materially harms model training

    "CRITICAL": 25  # was 20 — must be fixed before training
}