from pathlib import Path

import pandas as pd

from ..core.dataset import DatasetContainer
from .schema_normalizer import normalize_schema
from .dtype_normalizer import normalize_dtypes
from ..semantic.detector import detect_semantic_types

def load_csv(path: str):

    path = Path(path)

    if not path.exists():

        raise FileNotFoundError(
            f"Dataset not found: {path}"
        )

    df = pd.read_csv(path)
    df = normalize_schema(df)
    df = normalize_dtypes(df)
    semantic_types = detect_semantic_types(df)

    metadata = {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "memory_usage_mb": round(
            df.memory_usage(deep=True).sum() / 1024**2,
            2
        )
    }

    dataset = DatasetContainer(
        df=df,
        metadata=metadata,
        semantic_types=semantic_types
    )

    return dataset