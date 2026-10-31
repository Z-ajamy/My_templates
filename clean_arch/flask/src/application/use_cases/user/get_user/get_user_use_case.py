from src.application.protocols.uow import UnitOfWorkProtocol
from src.application.use_cases.exceptions import ResourceNotFoundError
from src.application.use_cases.user.get_user.dtos import (
    GetUserRequestDTO,
    GetUserResponseDTO,
)


class GetUserUseCase:
    def __init__(self, uow: UnitOfWorkProtocol):
        self.uow = uow

    def execute(self, request: GetUserRequestDTO) -> GetUserResponseDTO:
        with self.uow as db:
            user = db.user.get_by_id(id=request.id)
            if not user:
                raise ResourceNotFoundError(
                    resource_name="User",
                    id=request.id,
                    reason="User not found for get data",
                )
            res = GetUserResponseDTO(id=user.id, email=user.email.value)

            return res
