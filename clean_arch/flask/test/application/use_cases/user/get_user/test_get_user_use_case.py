from unittest.mock import Mock

import pytest

from src.application.use_cases.exceptions import ResourceNotFoundError
from src.application.use_cases.user.get_user.dtos import (
    GetUserRequestDTO,
    GetUserResponseDTO,
)
from src.application.use_cases.user.get_user.get_user_use_case import GetUserUseCase
from src.domain.shared.value_objs import Email


class MockUnitOfWork:
    def __init__(self):
        self.user = Mock()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, tb):
        pass


def test_get_user_success():
    uow = MockUnitOfWork()
    mock_user = Mock()
    mock_user.id = "123"
    mock_user.email = Email(value="test@domain.com")
    uow.user.get_by_id.return_value = mock_user

    use_case = GetUserUseCase(uow=uow)
    request = GetUserRequestDTO(id="123")

    response = use_case.execute(request)

    assert isinstance(response, GetUserResponseDTO)
    assert response.id == "123"
    assert response.email == "test@domain.com"
    uow.user.get_by_id.assert_called_once_with(id="123")


def test_get_user_not_found_raises_error():
    uow = MockUnitOfWork()
    uow.user.get_by_id.return_value = None

    use_case = GetUserUseCase(uow=uow)
    request = GetUserRequestDTO(id="999")

    with pytest.raises(ResourceNotFoundError) as exc_info:
        use_case.execute(request)

    assert exc_info.value.code == "USER_NOT_FOUND_ERROR"
    assert exc_info.value.context["id"] == "999"
