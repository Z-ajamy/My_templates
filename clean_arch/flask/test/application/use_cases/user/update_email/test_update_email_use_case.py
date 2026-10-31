from unittest.mock import Mock

import pytest

from src.application.use_cases.exceptions import ResourceNotFoundError
from src.application.use_cases.user.update_email.dtos import (
    UpdateEmailRequestDTO,
    UpdateEmailResponseDTO,
)
from src.application.use_cases.user.update_email.update_email_use_case import (
    UpdateEmailUseCase,
)
from src.domain.entities.user import User
from src.domain.shared.value_objs import Email


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


def test_update_email_success():
    uow = MockUnitOfWork()

    original_email = Email(value="old@domain.com")
    mock_user = User(id="123", name="Test User", email=original_email, version=0)

    uow.user.get_by_id.return_value = mock_user

    use_case = UpdateEmailUseCase(uow=uow)
    request = UpdateEmailRequestDTO(id="123", new_email="new@domain.com")

    response = use_case.execute(request)

    assert isinstance(response, UpdateEmailResponseDTO)
    assert response.id == "123"
    assert response.new_email == "new@domain.com"

    uow.user.get_by_id.assert_called_once_with(id="123")
    uow.user.save.assert_called_once()

    saved_user = uow.user.save.call_args[0][0]
    assert isinstance(saved_user, User)
    assert saved_user.email.value == "new@domain.com"
    assert saved_user.version == 1

    assert uow.commit_called is True


def test_update_email_user_not_found_raises_error():
    uow = MockUnitOfWork()
    uow.user.get_by_id.return_value = None

    use_case = UpdateEmailUseCase(uow=uow)
    request = UpdateEmailRequestDTO(id="999", new_email="new@domain.com")

    with pytest.raises(ResourceNotFoundError) as exc_info:
        use_case.execute(request)

    assert exc_info.value.code == "USER_NOT_FOUND_ERROR"
    assert exc_info.value.context["id"] == "999"

    assert uow.user.save.called is False
    assert uow.commit_called is False
