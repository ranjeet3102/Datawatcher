import pandas as pd


def is_categorical_column(
    series: pd.Series,
    unique_ratio_threshold: float = 0.5,
    max_unique_values: int = 100
) -> bool:


    if pd.api.types.is_numeric_dtype(series):

        return False

    if pd.api.types.is_datetime64_any_dtype(series):

        return False

    unique_count = series.nunique(dropna=True)

    total_count = len(series)

    unique_ratio = (
        unique_count / total_count
        if total_count > 0
        else 0
    )

    return (
        unique_count <= max_unique_values
        and unique_ratio <= unique_ratio_threshold
    )