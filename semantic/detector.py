import pandas as pd

from datawatcher.semantic.identifier import (
    is_identifier_column
)

from datawatcher.semantic.text_detector import (
    is_text_column
)

from datawatcher.semantic.datetime_detector import (
    is_datetime_column
)

from datawatcher.semantic.categorical import (
    is_categorical_column
)


def detect_semantic_types(
    df: pd.DataFrame
):
    """
    Detect semantic types for dataframe columns.
    """

    semantic_types = {}

    for column in df.columns:

        series = df[column]

        # Identifier detection
        if is_identifier_column(column):

            semantic_types[column] = "identifier"

            continue

        # Text detection
        if is_text_column(column):

            semantic_types[column] = "text"

            continue

        # Datetime detection
        if (
            pd.api.types.is_datetime64_any_dtype(series)
            or is_datetime_column(column)
        ):

            semantic_types[column] = "datetime"

            continue

        # Boolean detection
        if pd.api.types.is_bool_dtype(series):

            semantic_types[column] = "boolean"

            continue

        # Numeric detection
        if pd.api.types.is_numeric_dtype(series):

            semantic_types[column] = "numeric"

            continue

        # Explicit categorical detection
        if is_categorical_column(series):

            semantic_types[column] = "categorical"

            continue

        # Unknown fallback
        semantic_types[column] = "unknown"

    return semantic_types