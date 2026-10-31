from src.application.use_cases.exceptions import (
    ApplicationBaseError,
    ConcurrentModificationError,
    ResourceConflictError,
    ResourceNotFoundError,
)
from src.domain.exception.base_exception import ProjectBaseError


def test_application_base_error_inheritance():
    error = ApplicationBaseError(message="M", code="C", context=None)
    assert isinstance(error, ProjectBaseError)


def test_resource_not_found_error_initialization():
    error = ResourceNotFoundError(resource_name="User", id="123", reason="Deleted")
    assert "User" in error.message
    assert "'123'" in error.message
    assert error.code == "USER_NOT_FOUND_ERROR"
    assert error.context["resource_name"] == "User"
    assert error.context["id"] == "123"
    assert error.context["reason"] == "Deleted"


def test_resource_conflict_error_initialization():
    error = ResourceConflictError(
        resource_name="User", conflict_field="email", reason="Duplicate"
    )
    assert "User" in error.message
    assert "'email'" in error.message
    assert error.code == "USER_CONFLICT"
    assert error.context["resource_name"] == "User"
    assert error.context["conflict_field"] == "email"
    assert error.context["reason"] == "Duplicate"


def test_concurrent_modification_error_initialization():
    error = ConcurrentModificationError(
        resource_name="User", id="123", reason="Version mismatch"
    )
    assert "User" in error.message
    assert "id:123" in error.message
    assert error.code == "USER_CONCURRENT_MODIFICATION"
    assert error.context["resource_name"] == "User"
    assert error.context["id"] == "123"
    assert error.context["reason"] == "Version mismatch"
