from src.domain.exception.base_exception import DomainValidationError, ProjectBaseError
from src.domain.exception.entities_validation_exception import EntityValidationError
from src.domain.exception.value_obj_validation_exception import (
    ValueObjectValidationError,
)


def test_project_base_error_initialization() -> None:
    error = ProjectBaseError(
        message="Test error message", code="TEST_ERROR", context={"key": "value"}
    )
    assert error.message == "Test error message"
    assert error.code == "TEST_ERROR"
    assert error.context == {"key": "value"}
    assert str(error) == "Test error message"


def test_project_base_error_default_context() -> None:
    error = ProjectBaseError(message="Test", code="CODE", context=None)
    assert error.context == {}


def test_domain_validation_error_initialization() -> None:
    error = DomainValidationError(
        target_name="User", field="name", value=" ", reason="Cannot be empty"
    )
    assert "User" in error.message
    assert "name" in error.message
    assert error.code == "USER_VALIDATION_ERROR"
    assert error.context["target"] == "User"
    assert error.context["field"] == "name"
    assert error.context["rejected_value"] == " "
    assert error.context["reason"] == "Cannot be empty"


def test_entity_validation_error_inheritance() -> None:
    error = EntityValidationError(target_name="T", field="F", value="V")
    assert isinstance(error, DomainValidationError)
    assert isinstance(error, ProjectBaseError)


def test_value_object_validation_error_inheritance() -> None:
    error = ValueObjectValidationError(target_name="T", field="F", value="V")
    assert isinstance(error, DomainValidationError)
    assert isinstance(error, ProjectBaseError)
