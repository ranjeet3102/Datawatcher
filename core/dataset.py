class DatasetContainer:

    def __init__(
        self,
        df,
        metadata=None,
        schema=None,
        semantic_types=None
    ):

        self.df = df

        self.metadata = metadata or {}

        self.schema = schema or {}

        self.semantic_types = semantic_types or {}