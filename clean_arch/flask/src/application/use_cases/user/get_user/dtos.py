from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class GetUserRequestDTO:
    id: str


@dataclass(frozen=True, slots=True, kw_only=True)
class GetUserResponseDTO:
    id: str
    email: str
