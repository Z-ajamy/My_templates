from src.application.protocols.uow import UnitOfWorkProtocol
from src.application.use_cases.exceptions import ResourceConflictError
from src.application.use_cases.user.create_user.dtos import (
    CreateUserRequestDTO,
    CreateUserResponseDTO,
)
from src.domain.entities.user import User
from src.domain.shared.value_objs import Email


class CreateUserUseCase:
    def __init__(self, uow: UnitOfWorkProtocol):
        self.uow = uow

    def execute(self, request: CreateUserRequestDTO) -> CreateUserResponseDTO:
        with self.uow as db:
            email = Email(value=request.email)
            if db.user.get_by_email(email=email):
                raise ResourceConflictError(
                    resource_name="User",
                    conflict_field="Email",
                    reason="the email is exists",
                )

            user = User(name=request.name, email=email)

            db.user.save(user)
            db.commit()

            res = CreateUserResponseDTO(
                id=user.id, name=user.name, email=user.email.value
            )
            return res
