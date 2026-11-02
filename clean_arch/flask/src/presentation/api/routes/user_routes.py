from flask import Blueprint, current_app, request, jsonify, Response
from flask.views import MethodView

from src.application.use_cases.user.get_user.dtos import GetUserRequestDTO, GetUserResponseDTO
from src.application.use_cases.user.get_user.get_user_use_case import GetUserUseCase

from src.application.use_cases.user.create_user.dtos import CreateUserRequestDTO, CreateUserResponseDTO
from src.application.use_cases.user.create_user.create_user_use_case import CreateUserUseCase
from src.presentation.schemas.user.get_user import GetUserResponseSchema
from src.presentation.schemas.user.create_user import CreateUserRequestSchema, CreateUserResponseSchema
from src.application.use_cases.user.update_email.dtos import UpdateEmailRequestDTO, UpdateEmailResponseDTO
from src.application.use_cases.user.update_email.update_email_use_case import UpdateEmailUseCase
from src.presentation.schemas.user.update_email import UpdateEmailRequestSchema, UpdateEmailResponseSchema

from src.infrastructure.database.uow import SqlAlchemyUnitOfWork

user_bp = Blueprint("user", __name__, url_prefix="/users")
class UserAPI(MethodView):
    def get(self, user_id:str)->tuple[Response, int]:
        dto = GetUserRequestDTO(id=user_id)
        uow = SqlAlchemyUnitOfWork(session_maker=current_app.config["SESS_MKR"])
        use_case = GetUserUseCase(uow=uow)
        res: GetUserResponseDTO = use_case.execute(request=dto)

        response = GetUserResponseSchema(id=res.id, email=res.email, name=res.name)
        return jsonify(response.model_dump()), 200

    def post(self)->tuple[Response, int]:
        schema = CreateUserRequestSchema.model_validate(request.get_json())

        dto = CreateUserRequestDTO(name=schema.name, email=schema.email)
        uow = SqlAlchemyUnitOfWork(session_maker=current_app.config["SESS_MKR"])
        use_case = CreateUserUseCase(uow=uow)
        res:CreateUserResponseDTO = use_case.execute(request=dto)

        response = CreateUserResponseSchema(id=res.id, name=res.name, email=res.email)

        return jsonify(response.model_dump()), 201

    def patch(self, user_id: str)->tuple[Response, int]:
        schema = UpdateEmailRequestSchema.model_validate(request.get_json())
        
        dto = UpdateEmailRequestDTO(user_id=user_id, new_email=schema.new_email)
        uow = SqlAlchemyUnitOfWork(session_maker=current_app.config["SESS_MKR"])
        use_case = UpdateEmailUseCase(uow=uow)
        
        res:UpdateEmailResponseDTO = use_case.execute(dto)
        
        response = UpdateEmailResponseSchema(id=res.id, new_email=res.new_email)
        return jsonify(response.model_dump()), 200
        

user_view = UserAPI.as_view("user_api")

user_bp.add_url_rule('/', defaults={"user_id":None}, view_func=user_view, methods=["POST"])
user_bp.add_url_rule('/<user_id>', view_func=user_view, methods=['GET'])
user_bp.add_url_rule('/<user_id>/email', view_func=user_view, methods=['PATCH'])
