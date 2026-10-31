from dataclasses import dataclass

@dataclass(slots=True, frozen=True, kw_only=True)
class UpdateEmailRequestDTO:
    id:str
    new_email:str


@dataclass(slots=True, frozen=True, kw_only=True)
class UpdateEmailResponseDTO:
    id:str
    new_email:str

