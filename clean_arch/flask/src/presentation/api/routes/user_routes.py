from flask import Blueprint, Response, current_app, jsonify, request
from flask.views import MethodView

from src.application.use_cases.user.create_user.create_user_use_case import (
    CreateUserUseCase,
)
from src.application.use_cases.user.create_user.dtos import (
    CreateUserRequestDTO,
    CreateUserResponseDTO,
)
from src.application.use_cases.user.get_user.dtos import (
    GetUserRequestDTO,
    GetUserResponseDTO,
)
from src.application.use_cases.user.get_user.get_user_use_case import GetUserUseCase
from src.application.use_cases.user.update_email.dtos import (
    UpdateEmailRequestDTO,
    UpdateEmailResponseDTO,
)
from src.application.use_cases.user.update_email.update_email_use_case import (
    UpdateEmailUseCase,
)
from src.infrastructure.database.uow import SqlAlchemyUnitOfWork
from src.infrastructure.logger.setup import app_logger
from src.presentation.schemas.user.create_user import (
    CreateUserRequestSchema,
    CreateUserResponseSchema,
)
from src.presentation.schemas.user.get_user import GetUserResponseSchema
from src.presentation.schemas.user.update_email import (
    UpdateEmailRequestSchema,
    UpdateEmailResponseSchema,
)

user_bp = Blueprint("user", __name__, url_prefix="/users")


class UserAPI(MethodView):
    def get(self, user_id: str) -> tuple[Response, int]:
        """
        Get User by ID
        ---
        tags:
          - Users
        parameters:
          - in: path
            name: user_id
            type: string
            required: true
            description: The unique identifier of the user.
        responses:
          200:
            description: User retrieved successfully.
            schema:
              type: object
              properties:
                id:
                  type: string
                  example: "123e4567-e89b-12d3-a456-426614174000"
                email:
                  type: string
                  example: "engineer@domain.com"
                name:
                  type: string
                  example: "John Doe"
          404:
            description: Resource Not Found.
        """
        dto = GetUserRequestDTO(id=user_id)
        use_case = current_app.container.get_user_use_case()
        res: GetUserResponseDTO = use_case.execute(request=dto)

        response = GetUserResponseSchema(id=res.id, email=res.email, name=res.name)
        app_logger.info("Got User successfully")
        return jsonify(response.model_dump()), 200

    def post(self) -> tuple[Response, int]:
        """
        Create a new User
        ---
        tags:
          - Users
        parameters:
          - in: body
            name: body
            required: true
            description: User creation payload.
            schema:
              type: object
              required:
                - name
                - email
              properties:
                name:
                  type: string
                  minLength: 5
                  maxLength: 50
                  example: "Software Engineer"
                email:
                  type: string
                  format: email
                  example: "new.user@domain.com"
        responses:
          201:
            description: User created successfully.
            schema:
              type: object
              properties:
                id:
                  type: string
                name:
                  type: string
                email:
                  type: string
          409:
            description: Resource Conflict (e.g., Email already exists).
          422:
            description: Validation Error (Pydantic payload rejection).
        """
        schema = CreateUserRequestSchema.model_validate(request.get_json())

        dto = CreateUserRequestDTO(name=schema.name, email=schema.email)
        use_case = current_app.container.create_user_use_case()
        res: CreateUserResponseDTO = use_case.execute(request=dto)

        response = CreateUserResponseSchema(id=res.id, name=res.name, email=res.email)

        app_logger.info("Past User successfully")
        return jsonify(response.model_dump()), 201

    def patch(self, user_id: str) -> tuple[Response, int]:
        """
        Update User Email
        ---
        tags:
          - Users
        parameters:
          - in: path
            name: user_id
            type: string
            required: true
            description: The unique identifier of the user.
          - in: body
            name: body
            required: true
            schema:
              type: object
              required:
                - new_email
              properties:
                new_email:
                  type: string
                  format: email
                  example: "updated.email@domain.com"
        responses:
          200:
            description: Email updated successfully.
            schema:
              type: object
              properties:
                id:
                  type: string
                new_email:
                  type: string
          404:
            description: User not found.
          409:
            description: Resource Conflict (Email taken).
          422:
            description: Validation Error.
        """
        schema = UpdateEmailRequestSchema.model_validate(request.get_json())

        dto = UpdateEmailRequestDTO(id=user_id, new_email=schema.new_email)
        use_case = current_app.container.update_email_use_case()
        res: UpdateEmailResponseDTO = use_case.execute(dto)

        response = UpdateEmailResponseSchema(id=res.id, new_email=res.new_email)
        app_logger.info("Updated User successfully")
        return jsonify(response.model_dump()), 200


user_view = UserAPI.as_view("user_api")

user_bp.add_url_rule("/", view_func=user_view, methods=["POST"])
user_bp.add_url_rule("/<user_id>", view_func=user_view, methods=["GET"])
user_bp.add_url_rule("/<user_id>/email", view_func=user_view, methods=["PATCH"])
