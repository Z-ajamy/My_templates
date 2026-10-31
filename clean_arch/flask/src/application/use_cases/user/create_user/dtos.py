from dataclasses import dataclass


@dataclass(slots=True, frozen=True, kw_only=True)
class CreateUserRequestDTO:
    name: str
    email: str


@dataclass(slots=True, frozen=True, kw_only=True)
class CreateUserResponseDTO:
    id: str
    name: str
    email: str
