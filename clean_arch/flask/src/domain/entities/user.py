from __future__ import annotations

from dataclasses import dataclass, field, replace

# you can replace it with pydantic
from src.domain.entities.base import BaseEntity
from src.domain.exception.entities_validation_exception import EntityValidationError
from src.domain.shared.id_factory import create_uuid4
from src.domain.shared.value_objs import Email


@dataclass(slots=True, frozen=True, kw_only=True)
class User(BaseEntity):
    name: str
    email: Email
    version: int = field(
        default=0,
        metadata={"description": "the version for the mulithreads prosessing"},
    )

    def __post_init__(self) -> None:
        # raise in __init__ or __post_init__ will not create or replace the object
        if not isinstance(self.name, str):
            raise EntityValidationError(
                "User",
                "name",
                self.name,
                f"Expected str, got {type(self.name).__name__}",
            )
        if not self.name.strip():
            raise EntityValidationError(
                "User", "name", self.name, "Name cannot be empty"
            )

        if not isinstance(self.email, Email):
            raise EntityValidationError(
                entity_name="User",
                field="email",
                value=self.email,
                reason=f"the type of email is {type(self.email)} not Email type valid",
            )

        if not isinstance(self.version, int):
            raise EntityValidationError(
                "User",
                "version",
                self.version,
                f"Expected int, got {type(self.version).__name__}",
            )
        if self.version < 0:
            raise EntityValidationError(
                "User", "version", self.version, "Version cannot be negative"
            )

    def change_name(self, new_name: str) -> User:
        obj = replace(self, name=new_name, version=self.version + 1)
        return obj

    def change_email(self, new_email: str) -> User:
        em = Email(value=new_email)
        obj = replace(self, email=em, version=self.version + 1)
        return obj
