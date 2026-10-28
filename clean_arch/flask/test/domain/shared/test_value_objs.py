import pytest

from src.domain.exception.value_obj_validation_exception import (
    ValueObjectValidationError,
)
from src.domain.shared.value_objs import Email


def test_valid_email_creation():
    valid_email = "test.user_123@domain.com"
    email_obj = Email(value=valid_email)

    assert email_obj.value == valid_email


def test_invalid_email_raises_error():
    invalid_emails = [
        "plainaddress",
        "@no-local-part.com",
        "no-at.com",
        " spaces@domain.com ",
    ]

    for invalid in invalid_emails:
        with pytest.raises(ValueObjectValidationError):
            Email(value=invalid)
