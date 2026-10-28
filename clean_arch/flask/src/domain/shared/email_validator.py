from email_validator import validate_email, EmailNotValidError


def verify_email_syntax(email: str) -> bool:
    try:
        valid = validate_email(email)
        return True
    except EmailNotValidError as e:
        return False
