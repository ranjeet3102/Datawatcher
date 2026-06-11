TEXT_KEYWORDS = [
    "text",
    "review",
    "comment",
    "message",
    "description",
    "body",
    "feedback",
    "rating_comment",
    "opinion",
    "chat",
    "conversation",
    "reply",
    "response",
    "content",
    "remarks",
    "remark",
    "note",
    "notes",
    "details",
    "detail",
    "explanation",
    "issue_description",
    "complaint",
    "resolution",
    "post",
    "caption",
    "tweet",
    "answer",
    "feedback_text",
    "survey_response",
    "article",
    "paragraph",
    "statement",
    "story",
     "subject",
    "email_body",
    "review_text",
    "comment_text",
    "raw_text"
]


def is_text_column(
    column_name: str
) -> bool:

    column_name = column_name.lower()

    return any(
        keyword in column_name
        for keyword in TEXT_KEYWORDS
    )