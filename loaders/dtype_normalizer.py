import pandas as pd


DATETIME_KEYWORDS = [
    "date",
    "time",
    "timestamp",
    "created",
    "created_at",
    "updated",
    "updated_at",
    "modified",
    "modified_at",
    "birthday",
    "birthdate",
    "dob",
    "event_date",
    "event_time",
    "start_time",
    "start_date",
    "end_time",
    "end_date",
    "transaction_date",
    "purchase_date",
    "order_date",
    "payment_date",
    "join_date",
    "hire_date",
    "registration_date",
    "signup_date",
    "renewal_date",
    "schedule_date",
    "appointment_date",
    "meeting_date",
    "meeting_time",
    "log_date",
    "logged_at",
    "access_time",
    "_dt",
    "_date",
    "_time",
    "_ts",
    "ts",
    "_timestamp",
    "last_login",
    "last_seen",
    "last_active",
    "login_time",
    "logout_time",
    "login",
    "logout",
    "joined",
    "registered",
    "scheduled"
]

BOOLEAN_MAPPINGS = {
    "yes": True,
    "no": False,
    "true": True,
    "false": False,
    "y": True,
    "n": False,
    "1": True,
    "0": False
}


def looks_like_datetime_column(
    column_name: str
) -> bool:

    column_name = column_name.lower()

    return any(
        keyword in column_name
        for keyword in DATETIME_KEYWORDS
    )


def try_numeric_conversion(
    series: pd.Series
) -> pd.Series:
    

    try:

        converted = pd.to_numeric(
            series,
            errors="raise"
        )

        return converted

    except Exception:

        return series


def try_datetime_conversion(
    series: pd.Series
) -> pd.Series:
    
    try:

        converted = pd.to_datetime(
            series,
            errors="raise",
            format="mixed"
        )

        return converted

    except Exception:

        return series


def normalize_dtypes(
    df: pd.DataFrame
) -> pd.DataFrame:
   
    df = df.copy()

    for column in df.columns:

        series = df[column]

        if (
            pd.api.types.is_numeric_dtype(series)
            or pd.api.types.is_datetime64_any_dtype(series)
            or pd.api.types.is_bool_dtype(series)
        ):
            continue

        series = clean_empty_strings(series)
    
        converted_series = try_numeric_conversion(
            series
        )

        if converted_series.dtype != series.dtype:

            df[column] = converted_series

            continue

        converted_series = try_boolean_conversion(
            series
        )

        if converted_series.dtype != series.dtype:

            df[column] = converted_series

            continue

        if looks_like_datetime_column(column):

            converted_series = (
                try_datetime_conversion(series)
            )

            if (
                converted_series.dtype
                != series.dtype
            ):

                df[column] = converted_series

    return df

def try_boolean_conversion(
    series: pd.Series
) -> pd.Series:

    if not pd.api.types.is_object_dtype(series):

        return series

    normalized = (
        series.astype(str)
        .str.strip()
        .str.lower()
    )

    unique_values = set(
        normalized.dropna().unique()
    )

    allowed_values = set(
        BOOLEAN_MAPPINGS.keys()
    )

    if unique_values.issubset(allowed_values):

        return normalized.map(
            BOOLEAN_MAPPINGS
        ).astype("boolean")
    return series

def clean_empty_strings(
    series: pd.Series
) -> pd.Series:
    

    if not pd.api.types.is_object_dtype(series):

        return series

    return series.replace(
        r"^\s*$",
        pd.NA,
        regex=True
    )