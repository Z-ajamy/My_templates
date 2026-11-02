from src.domain.exception.base_exception import ProjectBaseError


class ApplicationBaseError(ProjectBaseError):
    pass


class ResourceNotFoundError(ApplicationBaseError):
    def __init__(
        self, resource_name: str, id: str | None = None, reason: str | None = None
    ):
        super().__init__(
            message=f"{resource_name} with identifier '{id or 'HIDED'}' was not found.",
            code=f"{resource_name.upper().replace(' ', '_')}_NOT_FOUND_ERROR",
            context={
                "resource_name": resource_name,
                "id": id,
                "reason": reason,
            },
        )


class ResourceConflictError(ApplicationBaseError):
    def __init__(
        self,
        resource_name: str,
        conflict_field: str | None = None,
        reason: str | None = None,
    ):
        super().__init__(
            message=f"Conflict detected in {resource_name} on field '{conflict_field or 'HIDED'}'.",
            code=f"{resource_name.upper().replace(' ', '_')}_CONFLICT",
            context={
                "resource_name": resource_name,
                "conflict_field": conflict_field,
                "reason": reason,
            },
        )


# the version error and it Raised in the Repo Unit Of Work
class ConcurrentModificationError(ApplicationBaseError):
    def __init__(
        self, resource_name: str, id: str | None = None, reason: str | None = None
    ):
        super().__init__(
            message=f"The {resource_name} (id:{id or 'HIDED'}) was modified by another process. Please retry.",
            code=f"{resource_name.upper().replace(' ', '_')}_CONCURRENT_MODIFICATION",
            context={"resource_name": resource_name, "id": id, "reason": reason},
        )
