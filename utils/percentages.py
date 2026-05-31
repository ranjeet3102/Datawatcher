# def calculate_percentage(
#     numerator: int,
#     denominator: int
# ) -> float:

#     if denominator == 0:
#         return 0.0

#     return round((numerator / denominator) * 100, 2)

def calculate_percentage(
    numerator: int,
    denominator: int
) -> float:

    if denominator == 0:
        return 0.0

    return float(
        round(
            (numerator / denominator) * 100,
            2
        )
    )