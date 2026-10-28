from dataclasses import dataclass, field
from typing import Any

from src.domain.shared.id_factory import create_uuid4


@dataclass(slots=True, frozen=True, kw_only=True)
class BaseEntity:
    id: str = field(
        default_factory=create_uuid4,
        metadata={"description": "the uniqe identifire of object"},
    )

    def __eq__(self, value: Any) -> bool:
        if not isinstance(value, type(self)):
            return False
        else:
            return value.id == self.id

    def __hash__(self) -> int:
        return hash(self.id)
