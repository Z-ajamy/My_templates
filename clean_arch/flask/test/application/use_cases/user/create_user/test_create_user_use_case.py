from unittest.mock import Mock

import pytest

from src.application.use_cases.exceptions import ResourceConflictError
from src.application.use_cases.user.create_user.create_user_use_case import (
    CreateUserUseCase,
)
from src.application.use_cases.user.create_user.dtos import (
    CreateUserRequestDTO,
    CreateUserResponseDTO,
)
from src.domain.entities.user import User


class MockUnitOfWork:
    def __init__(self):
        self.user = Mock()
        self.commit_called = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, tb):
        pass

    def commit(self):
        self.commit_called = True


def test_create_user_success():
    uow = MockUnitOfWork()
    uow.user.get_by_email.return_value = None

    use_case = CreateUserUseCase(uow=uow)
    request = CreateUserRequestDTO(name="Test User", email="test@domain.com")

    response = use_case.execute(request)

    assert isinstance(response, CreateUserResponseDTO)
    assert response.name == "Test User"
    assert response.email == "test@domain.com"
    assert hasattr(response, "id")

    uow.user.get_by_email.assert_called_once()
    uow.user.save.assert_called_once()

    saved_user = uow.user.save.call_args[0][0]
    assert isinstance(saved_user, User)
    assert saved_user.name == "Test User"
    assert saved_user.email.value == "test@domain.com"

    assert uow.commit_called is True


def test_create_user_conflict_raises_error() -> None:
    uow = MockUnitOfWork()
    uow.user.get_by_email.return_value = Mock(spec=User)

    use_case = CreateUserUseCase(uow=uow)
    request = CreateUserRequestDTO(name="Test User", email="test@domain.com")

    with pytest.raises(ResourceConflictError) as exc_info:
        use_case.execute(request)

    assert exc_info.value.code == "USER_CONFLICT"
    assert uow.user.save.called is False
    assert uow.commit_called is False
