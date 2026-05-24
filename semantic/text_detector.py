TEXT_KEYWORDS = [
    "text",
    "review",
    "comment",
    "message",
    "description"
]


def is_text_column(
    column_name: str
) -> bool:
    """
    Detect likely text columns.
    """

    column_name = column_name.lower()

    return any(
        keyword in column_name
        for keyword in TEXT_KEYWORDS
    )