from __future__ import annotations

from dataclasses import dataclass, field, replace

# you can replace it with pydantic
from src.domain.entities.base import BaseEntity
from src.domain.exception.entities_validation_exception import EntityValidationError
from src.domain.shared.value_objs import Email


@dataclass(slots=True, frozen=True, kw_only=True)
class User(BaseEntity):
    name: str
    email: Email
    version: int = field(
        default=0,
        metadata={"description": "optimistic locking version for concurrency control"},
    )

    def __post_init__(self) -> None:

        # raise key word in __init__ or __post_init__ will not create or replace the object
        if not self.name.strip():
            raise EntityValidationError(
                "User", "name", self.name, "Name cannot be empty"
            )

        if self.version < 0:
            raise EntityValidationError(
                "User", "version", self.version, "Version cannot be negative"
            )

    def change_name(self, new_name: str) -> User:
        obj = replace(self, name=new_name, version=self.version + 1)
        return obj

    def change_email(self, new_email: Email) -> User:
        obj = replace(self, email=new_email, version=self.version + 1)
        return obj

