from typing import Any


class ProjectBaseError(Exception):
    def __init__(self, message: str, code: str, context: dict[str, Any] | None):

        super().__init__(message)
        self.message: str = message
        self.code: str = code
        self.context: dict[str, Any] | None = context or {}


class DomainValidationError(ProjectBaseError):
    def __init__(
        self, target_name: str, field: str, value: Any, reason: str | None = None
    ):
        super().__init__(
            message=f"Validation failed for {target_name}.{field}.",
            code=f"{target_name.upper()}_VALIDATION_ERROR",
            context={
                "target": target_name,
                "field": field,
                "rejected_value": value,
                "reason": reason,
            },
        )
