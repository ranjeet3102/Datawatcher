DATETIME_KEYWORDS = [
    "date",
    "time",
    "timestamp",
    "created",
    "updated",
    "dob"
]


def is_datetime_column(
    column_name: str
) -> bool:
    """
    Detect likely datetime columns.
    """

    column_name = column_name.lower()

    return any(
        keyword in column_name
        for keyword in DATETIME_KEYWORDS
    )