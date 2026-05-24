from datawatcher.loaders.csv_loader import load_csv


def load_dataset(path: str):

    if path.endswith(".csv"):

        return load_csv(path)

    else:

        raise ValueError(
            "Unsupported file format"
        )
    