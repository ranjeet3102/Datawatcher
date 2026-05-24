IDENTIFIER_KEYWORDS = [
    "id",
    "uuid",
    "customer_id",
    "user_id",
    "email",
    "phone",
    "account",
    "customer"
]


def is_identifier_column(
    column_name: str
) -> bool:
    """
    Detect likely identifier columns.
    """

    column_name = column_name.lower()

    return any(
        keyword in column_name
        for keyword in IDENTIFIER_KEYWORDS
    )