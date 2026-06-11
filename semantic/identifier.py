IDENTIFIER_KEYWORDS = [
    "id",
    "uuid",
    "customer_id",
    "user_id",
    "email",
    "phone",
    "account",
    "customer",
    "_id",
    "guid",
    "key",
    "cust_id",
    "userid",
    "user",
    "account_id",
    "email_address",
    "phone_number",
    "mobile_number",
    "mobile",
    "account_number",
    "account_num",
    "contact",
    "employee_id",
    "emp_id",
    "staff_id",
    "product_id",
    "sku",
    "item_id",
    "order_id",
    "transaction_id",
    "invoice_id",
    "payment_id",
    "address_id",
    "location_id",
    "patient_id",
    "member_id",
    "card_number",
    "session_id",
    "api_key",
    "device_id"
]


def is_identifier_column(
    column_name: str
) -> bool:
   
    column_name = column_name.lower()

    return any(
        keyword in column_name
        for keyword in IDENTIFIER_KEYWORDS
    )