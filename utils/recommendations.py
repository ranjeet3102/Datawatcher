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