def calculate_severity(
    value: float,
    low_threshold: float,
    medium_threshold: float
) -> str:

    if value == 0:
        return "info"

    if value < low_threshold:
        return "low"

    if value < medium_threshold:
        return "medium"

    return "high"

