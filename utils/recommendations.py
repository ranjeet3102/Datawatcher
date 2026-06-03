def missing_value_recommendation(
    missing_percentage: float
) -> str:

    if missing_percentage == 0:
        return "No missing values detected."

    if missing_percentage < 5:
        return "Minor missing values detected. Consider simple imputation."

    if missing_percentage < 20:
        return (
            "Moderate missing values detected. "
            "Investigate feature-level imputation strategies."
        )

    return (
        "High missing value percentage detected. "
        "Feature removal or advanced imputation may be required."
    )

def duplicate_recommendation(
    duplicate_percentage: float
) -> str:
    
    if duplicate_percentage == 0:
        return "No duplicate rows detected."

    if duplicate_percentage < 1:
        return "Small number of duplicate rows detected. Review before training."

    if duplicate_percentage < 10:
        return (
            "Moderate duplicate row percentage detected. "
            "Consider removing duplicates."
        )

    return (
        "High duplicate row percentage detected. "
        "Dataset cleanup is strongly recommended."
    )


def constant_feature_recommendation(
    count: int
) -> str:

    if count == 0:

        return (
            "No constant features detected."
        )

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
            "Review near-constant features "
            "for potential removal."
        )

    return (
        "Multiple near-constant features detected. "
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

        return (
            "No low-variance features detected."
        )

    if count <= 2:

        return (
            "Review low-variance features for potential removal."
        )

    return (
        "Multiple low-variance features detected. "
        "Feature selection is recommended."
    )


def skewness_recommendation(
    count: int
) -> str:

    if count == 0:
        return (
            "No highly skewed features detected."
        )

    if count <= 2:
        return (
            "Review skewed features. "
            "Transformation may improve model performance."
        )

    return (
        "Multiple highly skewed features detected. "
        "Consider log or power transformations."
    )

def kurtosis_recommendation(
    count: int
) -> str:

    if count == 0:

        return (
            "No heavy-tailed features detected."
        )

    if count <= 2:

        return (
            "Review heavy-tailed features. "
            "Outlier analysis may be useful."
        )

    return (
        "Multiple heavy-tailed features detected. "
        "Consider transformation and outlier treatment."
    )

def outlier_recommendation(
    count: int
) -> str:

    if count == 0:

        return (
            "No significant outliers detected."
        )

    if count < 10:

        return (
            "Small number of outliers detected. "
            "Review affected features."
        )

    return (
        "Large number of outliers detected. "
        "Consider outlier treatment or transformation."
    )

def rare_category_recommendation(
    count: int
) -> str:

    if count == 0:

        return (
            "No rare categories detected."
        )

    if count <= 5:

        return (
            "Review rare categories. "
            "Grouping may improve model stability."
        )

    return (
        "Many rare categories detected. "
        "Consider category consolidation."
    )


def category_imbalance_recommendation(
    count: int
) -> str:

    if count == 0:

        return (
            "No significant category imbalance detected."
        )

    if count <= 2:

        return (
            "Review imbalanced categorical features."
        )

    return (
        "Multiple imbalanced categorical features detected. "
        "Consider feature engineering strategies."
    )

def cardinality_recommendation(
    count: int
) -> str:

    if count == 0:

        return (
            "No high-cardinality features detected."
        )

    if count <= 2:

        return (
            "Review high-cardinality features before encoding."
        )

    return (
        "Multiple high-cardinality features detected. "
        "Consider hashing, target encoding, or removal."
    )
    

def identifier_risk_recommendation(
    count: int
) -> str:

    if count == 0:

        return (
            "No identifier-risk features detected."
        )

    if count <= 2:

        return (
            "Review identifier-like features before training."
        )

    return (
        "Multiple identifier-risk features detected. "
        "Feature removal is recommended."
    )


def target_validation_recommendation(
    passed: bool
) -> str:

    if passed:

        return (
            "Target column is suitable for modeling."
        )

    return (
        "Review target column configuration."
    )


def class_imbalance_recommendation(
    imbalanced: bool
) -> str:

    if not imbalanced:

        return (
            "Target distribution appears balanced."
        )

    return (
        "Target class imbalance detected. "
        "Consider class weighting, resampling, or specialized metrics."
    )

def leakage_recommendation(
    count: int
) -> str:

    if count == 0:

        return (
            "No obvious leakage features detected."
        )

    if count <= 2:

        return (
            "Review potential leakage features before training."
        )

    return (
        "Multiple potential leakage features detected. "
        "Feature removal is strongly recommended."
    )