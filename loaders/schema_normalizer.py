import re
import pandas as pd


def normalize_column_name(column: str) -> str:
    
    column = str(column)

    column = column.strip()

    column = column.lower()

    column = re.sub(r"[ -]+", "_", column)

    column = re.sub(r"[^a-zA-Z0-9_]", "", column)

    column = re.sub(r"_+", "_", column)

    column = column.strip("_")

    return column


def normalize_schema(df: pd.DataFrame) -> pd.DataFrame:
    
    df = df.copy()

    normalized_columns = [
        normalize_column_name(col)
        for col in df.columns
    ]

    df.columns = normalized_columns

    return df