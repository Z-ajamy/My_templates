from dataclasses import dataclass

from src.domain.exception.value_obj_validation_exception import (
    ValueObjectValidationError,
)
from src.domain.shared.email_validator import verify_email_syntax


# value object: is an obj that identifire by it's value and mostally has no id attribute
@dataclass(slots=True, frozen=True, kw_only=True)
class Email:
    value: str

    def __post_init__(self) -> None:

        if not verify_email_syntax(self.value):
            raise ValueObjectValidationError(
                target_name="Email",
                field="value",
                value=self.value,
                reason="Invalid email pattern",
            )
