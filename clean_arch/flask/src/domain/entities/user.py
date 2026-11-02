from __future__ import annotations

from dataclasses import dataclass, replace

# you can replace it with pydantic
from src.domain.entities.base import BaseEntity
from src.domain.exception.entities_validation_exception import EntityValidationError
from src.domain.shared.value_objs import Email


# لو شلت eq=False فان الداتاكلاس هيعمل افررايت لل eq بتاع ال Base
@dataclass(slots=True, frozen=True, kw_only=True, eq=False)
class User(BaseEntity):
    name: str
    email: Email

    def __post_init__(self) -> None:

        # raise key word in __init__ or __post_init__ will not create or replace the object
        if not self.name.strip():
            raise EntityValidationError(
                "User", "name", self.name, "Name cannot be empty"
            )
        if len(self.name) > 50:
            raise EntityValidationError(
                "User", "name", self.name, "Name must be <50 char"
            )

    def change_name(self, new_name: str) -> User:
        obj = replace(self, name=new_name)
        return obj

    def change_email(self, new_email: Email) -> User:
        obj = replace(self, email=new_email)
        return obj
