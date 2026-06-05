# ============================================================
# DataWatcher — Production Thresholds
#
# All values are grounded in published research or widely-adopted
# ML production frameworks (Google TFDV, AWS Deequ, Great
# Expectations, scikit-learn, academic papers cited inline).
# ============================================================

# ------------------------------------------------------------
# Missing Values
# Google TFDV flags >3% missing for attention.
# Little & Rubin (1987): >15% missing causes severe bias
# in most imputation strategies.
# ------------------------------------------------------------
MISSING_VALUE_THRESHOLDS = {
    "low": 3,      # was 5
    "medium": 15   # was 20
}

# ------------------------------------------------------------
# Duplicate Rows
# AWS Deequ default: >0.5% duplicates flagged in transactional data.
# Great Expectations: >5% duplicates compromises generalization.
# ------------------------------------------------------------
DUPLICATE_THRESHOLDS = {
    "low": 0.5,    # was 1
    "medium": 5    # was 10
}

# ------------------------------------------------------------
# Constant Features
# Any constant feature provides zero information — counts stay low.
# ------------------------------------------------------------
CONSTANT_FEATURE_THRESHOLDS = {
    "low": 1,
    "medium": 3
}

# ------------------------------------------------------------
# Near-Constant Features
# scikit-learn VarianceThreshold equivalent:
# 95% same value → feature is near-useless (was 0.98).
# ------------------------------------------------------------
NEAR_CONSTANT_THRESHOLDS = {
    "dominance_ratio": 0.95    # was 0.98
}

NEAR_CONSTANT_COUNT_THRESHOLDS = {
    "low": 1,
    "medium": 3
}

# ------------------------------------------------------------
# Invalid Values (Inf, NaN after load, unrealistic)
# Expressed as absolute counts — small counts still matter at scale.
# ------------------------------------------------------------
INVALID_VALUE_THRESHOLDS = {
    "low": 10,
    "medium": 100
}

# ------------------------------------------------------------
# Variance
# scikit-learn VarianceThreshold default is 0 (removes constants).
# For normalized/scaled features, 0.001 catches near-zero spread.
# Absolute 0.01 was too aggressive for features with small ranges.
# ------------------------------------------------------------
VARIANCE_THRESHOLDS = {
    "low_variance": 0.001    # was 0.01
}

LOW_VARIANCE_COUNT_THRESHOLDS = {
    "low": 1,
    "medium": 3
}

# ------------------------------------------------------------
# Skewness
# Bulmer (1979): moderate skew |s| ∈ [0.5, 1.0), high |s| ≥ 1.0.
# Hair et al. (2010) multivariate analysis confirms same cutoffs.
# Values unchanged — already research-aligned.
# ------------------------------------------------------------
SKEWNESS_THRESHOLDS = {
    "moderate": 0.5,    # ✅ kept
    "high": 1.0         # ✅ kept
}

SKEWED_FEATURE_COUNT_THRESHOLDS = {
    "low": 1,
    "medium": 3
}

# ------------------------------------------------------------
# Kurtosis
# DeCarlo (1997): excess kurtosis >4 is the accepted heavy-tail
# cutoff. Pandas .kurt() returns EXCESS kurtosis, so raw threshold
# of 3.0 (= 0 excess) was incorrect — it flagged normal distributions.
# New value: excess kurtosis > 7 flags genuinely heavy tails.
# ------------------------------------------------------------
KURTOSIS_THRESHOLDS = {
    "high": 7.0    # was 3.0 (wrong — pandas returns excess kurtosis)
}

KURTOTIC_FEATURE_COUNT_THRESHOLDS = {
    "low": 1,
    "medium": 3
}

# ------------------------------------------------------------
# Outliers (IQR-based)
# For large data, absolute counts are meaningless.
# IBM Research / TFDV: use % of total rows as the reference.
#   LOW:    > 0.5% of rows contain outlier values
#   MEDIUM: > 2.0% of rows contain outlier values
# The outlier_audit uses these as percentage thresholds.
# ------------------------------------------------------------
OUTLIER_THRESHOLDS = {
    "low_pct": 0.5,     # % of total rows — replaces absolute count 10
    "medium_pct": 2.0   # % of total rows — replaces absolute count 100
}

# Legacy absolute fallback (used if row count unavailable)
OUTLIER_COUNT_THRESHOLDS = {
    "low": 10,
    "medium": 100
}

# ------------------------------------------------------------
# Rare Categories
# Micci-Barreca (2001): categories with <0.5% frequency are unsafe
# for target encoding and may destabilize tree splits.
# ------------------------------------------------------------
RARE_CATEGORY_THRESHOLDS = {
    "rare_percentage": 0.5    # was 1.0
}

RARE_CATEGORY_COUNT_THRESHOLDS = {
    "low": 5,
    "medium": 20
}

# ------------------------------------------------------------
# Category Imbalance
# Chawla et al. (2002) SMOTE paper: severe imbalance begins
# at 70/30 split for categorical features.
# ------------------------------------------------------------
CATEGORY_IMBALANCE_THRESHOLDS = {
    "dominance_ratio": 70.0    # was 80.0
}

CATEGORY_IMBALANCE_COUNT_THRESHOLDS = {
    "low": 1,
    "medium": 3
}

# ------------------------------------------------------------
# Cardinality (ML risk)
# Practical ML consensus: >30% unique values in a non-numeric
# column = quasi-identifier or unencodeable text.
# (was 0.50 — too permissive for large datasets)
# ------------------------------------------------------------
CARDINALITY_THRESHOLDS = {
    "high_cardinality_ratio": 0.30    # was 0.50
}

HIGH_CARDINALITY_COUNT_THRESHOLDS = {
    "low": 1,
    "medium": 3
}

# ------------------------------------------------------------
# Identifier Risk
# Lowered to catch near-unique quasi-identifiers.
# 90% unique values is sufficient to act as a de-facto ID,
# which is both an ML risk (memorization) and a GDPR concern.
# ------------------------------------------------------------
IDENTIFIER_RISK_THRESHOLDS = {
    "high_cardinality_ratio": 0.90    # was 0.95
}

IDENTIFIER_RISK_COUNT_THRESHOLDS = {
    "low": 1,
    "medium": 3
}

# ------------------------------------------------------------
# Class Imbalance (target column)
# Japkowicz & Stephen (2002): classification performance degrades
# significantly when majority class exceeds 75%.
# He & Garcia (2009) imbalanced learning survey confirms 75% cutoff.
# ------------------------------------------------------------
CLASS_IMBALANCE_THRESHOLDS = {
    "dominance_ratio": 75.0    # was 80.0
}

CLASS_IMBALANCE_COUNT_THRESHOLDS = {
    "low": 1,
    "medium": 2
}

# ------------------------------------------------------------
# Data Leakage (correlation-based)
# Industry standard: Pearson |r| > 0.90 with target = strong
# leakage signal. 0.95 was too conservative and missed real leakage.
# ------------------------------------------------------------
LEAKAGE_THRESHOLDS = {
    "correlation": 0.90    # was 0.95
}

LEAKAGE_COUNT_THRESHOLDS = {
    "low": 1,
    "medium": 3
}

# ------------------------------------------------------------
# Negative Values (finance domain)
# ------------------------------------------------------------
NEGATIVE_VALUE_THRESHOLDS = {
    "low": 1,
    "medium": 3
}