# ============================================================
# DataWatcher — Human-Readable Recommendations
#
# Text thresholds updated to match the new research-backed
# values in utils/thresholds.py.
# ============================================================


def missing_value_recommendation(
    missing_percentage: float
) -> str:

    if missing_percentage == 0:
        return "No missing values detected."

    if missing_percentage < 3:
        return "Minimal missing values (<3%). Safe to proceed with simple imputation."

    if missing_percentage < 15:
        return (
            "Moderate missing values detected (3–15%). "
            "Investigate feature-level imputation strategies (median, KNN, or MICE)."
        )

    return (
        "High missing value rate (>15%) detected. "
        "Feature removal or advanced imputation required — exceeds Little & Rubin (1987) safe threshold."
    )


def duplicate_recommendation(
    duplicate_percentage: float
) -> str:

    if duplicate_percentage == 0:
        return "No duplicate rows detected."

    if duplicate_percentage < 0.5:
        return "Minimal duplicates (<0.5%). Review before training."

    if duplicate_percentage < 5:
        return (
            "Moderate duplicate row percentage (0.5–5%) detected. "
            "Remove duplicates before training."
        )

    return (
        "High duplicate row percentage (>5%) detected. "
        "Dataset cleanup is strongly recommended — exceeds Great Expectations production threshold."
    )


def constant_feature_recommendation(
    count: int
) -> str:

    if count == 0:
        return "No constant features detected."

    if count <= 2:
        return (
            "Review constant features and "
            "consider removing them."
        )

    return (
        "Multiple constant features detected. "
        "Feature cleanup is recommended."
    )


def near_constant_recommendation(
    count: int
) -> str:

    if count == 0:
        return "No near-constant features detected."

    if count <= 2:
        return (
            "Review near-constant features (>95% single value). "
            "These provide near-zero information for most models."
        )

    return (
        "Multiple near-constant features detected (>95% single value). "
        "Feature reduction is recommended."
    )


def invalid_value_recommendation(
    count: int
) -> str:

    if count == 0:
        return "No invalid values detected."

    if count < 10:
        return (
            "Small number of invalid values detected. "
            "Review affected columns."
        )

    return (
        "Significant invalid values detected. "
        "Data cleansing is recommended."
    )


def variance_recommendation(
    count: int
) -> str:

    if count == 0:
        return "No low-variance features detected."

    if count <= 2:
        return (
            "Review low-variance features (variance < 0.001) for potential removal."
        )

    return (
        "Multiple low-variance features detected. "
        "Feature selection is recommended."
    )


def skewness_recommendation(
    count: int
) -> str:

    if count == 0:
        return "No highly skewed features detected."

    if count <= 2:
        return (
            "Review skewed features (|skew| ≥ 1.0). "
            "Log or power transformations may improve model performance."
        )

    return (
        "Multiple highly skewed features detected. "
        "Consider log, Box-Cox, or Yeo-Johnson transformations (Hair et al., 2010)."
    )


def kurtosis_recommendation(
    count: int
) -> str:

    if count == 0:
        return "No heavy-tailed features detected."

    if count <= 2:
        return (
            "Review heavy-tailed features (excess kurtosis > 7). "
            "Outlier analysis and winsorization may be useful."
        )

    return (
        "Multiple heavy-tailed features detected (excess kurtosis > 7). "
        "Consider transformation and outlier treatment (DeCarlo, 1997)."
    )


def outlier_recommendation(
    count: int
) -> str:

    if count == 0:
        return "No significant outliers detected."

    if count < 10:
        return (
            "Small number of outliers detected. "
            "Review affected features."
        )

    return (
        "Large number of outliers detected. "
        "Consider outlier treatment or transformation."
    )


def outlier_pct_recommendation(
    outlier_pct: float
) -> str:
    """
    Percentage-based outlier recommendation for large datasets.
    """

    if outlier_pct == 0:
        return "No significant outliers detected."

    if outlier_pct < 0.5:
        return (
            f"Minimal outliers ({outlier_pct:.2f}% of rows). "
            "Review affected features."
        )

    if outlier_pct < 2.0:
        return (
            f"Moderate outlier rate ({outlier_pct:.2f}% of rows). "
            "Winsorization or robust scaling recommended."
        )

    return (
        f"High outlier rate ({outlier_pct:.2f}% of rows). "
        "Consider outlier treatment, transformation, or robust model selection."
    )


def rare_category_recommendation(
    count: int
) -> str:

    if count == 0:
        return "No rare categories detected."

    if count <= 5:
        return (
            "Review rare categories (<0.5% frequency). "
            "Grouping into 'Other' improves encoding stability (Micci-Barreca, 2001)."
        )

    return (
        "Many rare categories detected (<0.5% frequency). "
        "Category consolidation is strongly recommended."
    )


def category_imbalance_recommendation(
    count: int
) -> str:

    if count == 0:
        return "No significant category imbalance detected."

    if count <= 2:
        return (
            "Review imbalanced categorical features (dominant category >70%)."
        )

    return (
        "Multiple imbalanced categorical features detected (dominant >70%). "
        "Consider feature engineering or binning strategies."
    )


def cardinality_recommendation(
    count: int
) -> str:

    if count == 0:
        return "No high-cardinality features detected."

    if count <= 2:
        return (
            "Review high-cardinality features (>30% unique values) before encoding."
        )

    return (
        "Multiple high-cardinality features detected (>30% unique values). "
        "Consider hashing, target encoding, or removal."
    )


def identifier_risk_recommendation(
    count: int
) -> str:

    if count == 0:
        return "No identifier-risk features detected."

    if count <= 2:
        return (
            "Review identifier-like features (>90% unique values) before training. "
            "These may cause memorization and are a GDPR concern."
        )

    return (
        "Multiple identifier-risk features detected (>90% unique values). "
        "Feature removal is strongly recommended."
    )


def target_validation_recommendation(
    passed: bool
) -> str:

    if passed:
        return "Target column is suitable for modeling."

    return "Review target column configuration."


def class_imbalance_recommendation(
    imbalanced: bool
) -> str:

    if not imbalanced:
        return "Target distribution appears balanced."

    return (
        "Target class imbalance detected (majority class >75%). "
        "Consider class weighting, SMOTE resampling, or F1/AUC metrics "
        "(Japkowicz & Stephen, 2002)."
    )


def leakage_recommendation(
    count: int
) -> str:

    if count == 0:
        return "No obvious leakage features detected."

    if count <= 2:
        return (
            "Review potential leakage features (|r| > 0.90 with target) before training."
        )

    return (
        "Multiple potential leakage features detected (|r| > 0.90 with target). "
        "Feature removal is strongly recommended."
    )


def negative_value_recommendation(
    count: int
) -> str:

    if count == 0:
        return "No unexpected negative values detected."

    if count <= 2:
        return "Review columns containing negative values."

    return (
        "Multiple columns contain negative values. "
        "Validate business rules and data quality."
    )


def currency_consistency_recommendation(
    inconsistent_columns: int
) -> str:

    if inconsistent_columns == 0:
        return "No currency consistency issues detected."

    if inconsistent_columns <= 2:
        return (
            "Review currency formatting and standardize currency values."
        )

    return (
        "Multiple currency consistency issues detected. "
        "Consider applying currency normalization rules."
    )


def interest_rate_recommendation(
    invalid_columns: int
) -> str:

    if invalid_columns == 0:
        return "Interest rate values appear valid."

    return (
        "Review interest rate columns for "
        "negative or unrealistic values."
    )


def balance_consistency_recommendation(
    inconsistent_rows: int
) -> str:

    if inconsistent_rows == 0:
        return "Balance relationships appear consistent."

    return (
        "Balance inconsistencies detected. "
        "Review transaction calculations."
    )


def duplicate_timestamp_recommendation(
    duplicate_count: int
) -> str:

    if duplicate_count == 0:
        return "No duplicate timestamps detected."

    return (
        "Duplicate timestamps detected. "
        "Review aggregation and data collection logic."
    )