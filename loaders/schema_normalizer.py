import re
import pandas as pd


def normalize_column_name(column: str) -> str:
    """
    Normalize a single column name into
    canonical snake_case format.
    """

    column = str(column)

    # Remove leading/trailing whitespace
    column = column.strip()

    # Lowercase
    column = column.lower()

    # Replace spaces and hyphens
    column = re.sub(r"[ -]+", "_", column)

    # Remove special characters
    column = re.sub(r"[^a-zA-Z0-9_]", "", column)

    # Remove repeated underscores
    column = re.sub(r"_+", "_", column)

    # Remove leading/trailing underscores
    column = column.strip("_")

    return column


def normalize_schema(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize all dataframe column names.
    """

    df = df.copy()

    normalized_columns = [
        normalize_column_name(col)
        for col in df.columns
    ]

    df.columns = normalized_columns

    return df