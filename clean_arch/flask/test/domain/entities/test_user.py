import pytest

from src.domain.entities.user import User
from src.domain.exception.entities_validation_exception import EntityValidationError
from src.domain.shared.id_factory import create_uuid4
from src.domain.shared.value_objs import Email


def test_user_entity_creation_success():
    user_id = create_uuid4()
    email_vo = Email(value="ali@gmail.com")
    user = User(id=user_id, name="Ali", email=email_vo)

    assert user.id == user_id
    assert user.name == "Ali"
    assert user.email.value == "ali@gmail.com"
    assert user.version == 0


def test_user_creation_empty_name_raises_error():
    email_vo = Email(value="ali@gmail.com")
    with pytest.raises(EntityValidationError):
        User(name="   ", email=email_vo)


def test_user_creation_negative_version_raises_error():
    email_vo = Email(value="ali@gmail.com")
    with pytest.raises(EntityValidationError):
        User(name="Ali", email=email_vo, version=-1)


def test_user_change_name_increments_version():
    email_vo = Email(value="ali@gmail.com")
    user = User(name="Ali", email=email_vo)
    new_user = user.change_name("Ahmed")

    assert new_user.name == "Ahmed"
    assert new_user.version == user.version + 1
    assert new_user.id == user.id


def test_user_change_email_increments_version():
    email_vo = Email(value="ali@gmail.com")
    user = User(name="Ali", email=email_vo)
    new_user = user.change_email(Email(value="ahmed@gmail.com"))

    assert isinstance(new_user.email, Email)
    assert new_user.email.value == "ahmed@gmail.com"
    assert new_user.version == user.version + 1
    assert new_user.id == user.id
