from src.application.protocols.uow import UnitOfWorkProtocol
from src.application.use_cases.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
)
from src.application.use_cases.user.update_email.dtos import (
    UpdateEmailRequestDTO,
    UpdateEmailResponseDTO,
)
from src.domain.shared.value_objs import Email


class UpdateEmailUseCase:
    def __init__(self, uow: UnitOfWorkProtocol):
        self.uow = uow

    def execute(self, request: UpdateEmailRequestDTO) -> UpdateEmailResponseDTO:
        # TOCTOU
        new_email = Email(value=request.new_email)
        with self.uow as db:
            user = db.user.get_by_id(id=request.id)
            if not user:
                raise ResourceNotFoundError(
                    resource_name="User",
                    id=request.id,
                    reason="User not found for email update",
                )

            existing_user = db.user.get_by_email(email=new_email)
            if existing_user and existing_user != user: #existing_user.id != user.id
                raise ResourceConflictError(
                    resource_name="User",
                    conflict_field="Email",
                    reason="The requested email is already registered to another user",
                )

            updated_user = user.change_email(new_email=new_email)

            db.user.save(updated_user)
            db.commit()
            res = UpdateEmailResponseDTO(
                id=updated_user.id, new_email=updated_user.email.value
            )

            return res
