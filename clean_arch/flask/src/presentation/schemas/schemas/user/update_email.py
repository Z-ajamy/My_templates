from pydantic import BaseModel, ConfigDict, EmailStr


class UpdateEmailRequestSchema(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=False,
        str_strip_whitespace=True,
        strict=True,
    )
    new_email: EmailStr
