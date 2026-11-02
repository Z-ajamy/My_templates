from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CreateUserRequestSchema(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=False,
        str_strip_whitespace=True,
        strict=True,
    )
    name: str = Field(min_length=5, max_length=50)
    email: EmailStr


class CreateUserResponseSchema(BaseModel):
    id: str
    email: EmailStr
    name: str
