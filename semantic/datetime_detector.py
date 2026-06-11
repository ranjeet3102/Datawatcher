DATETIME_KEYWORDS = [
    "date",
    "time",
    "datetime",
    "timestamp",
    "created",
    "created_at",
    "updated",
    "updated_at",
    "modified",
    "modified_at",
    "dob",
    "birthdate",
    "birthday",
    "start_date",
    "start_time",
    "start_datetime",
    "end_date",
    "end_time",
    "end_datetime",
    "event_date",
    "event_time",
    "event_timestamp",
    "transaction_date",
    "transaction_time",
    "purchase_date",
    "order_date",
    "payment_date",
    "invoice_date",
    "signup_date",
    "registration_date",
    "join_date",
    "joined_at",
    "renewal_date",
    "hire_date",
    "termination_date",
    "schedule_date",
    "appointment_date",
    "meeting_date",
    "meeting_time",
    "log_date",
    "logged_at",
    "access_time",
    "login_time",
    "logout_time",
    "last_login",
    "last_seen",
    "last_active",
    "_date",
    "_time",
    "_datetime",
    "_timestamp",
    "_dt",
    "_ts",
    "dt_",
    "ts_"
]


def is_datetime_column(
    column_name: str
) -> bool:

    column_name = column_name.lower()

    return any(
        keyword in column_name
        for keyword in DATETIME_KEYWORDS
    )