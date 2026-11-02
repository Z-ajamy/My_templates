from flask import Flask, Response, jsonify
from pydantic import ValidationError

from src.application.use_cases.exceptions import (
    ConcurrentModificationError,
    ResourceConflictError,
    ResourceNotFoundError,
)
from src.domain.exception.base_exception import DomainValidationError


def register_error_handlers(app: Flask) -> None:

    @app.errorhandler(ValidationError)
    def handle_pydantic_validation(error: ValidationError) -> tuple[Response, int]:
        return jsonify({"error": "Validation Error", "details": error.errors()}), 422

    @app.errorhandler(ResourceNotFoundError)
    def handle_not_found(error: ResourceNotFoundError) -> tuple[Response, int]:
        return jsonify({"error": error.code, "message": error.message}), 404

    @app.errorhandler(ResourceConflictError)
    def handle_conflict(error: ResourceConflictError) -> tuple[Response, int]:
        return jsonify({"error": error.code, "message": error.message}), 409

    @app.errorhandler(ConcurrentModificationError)
    def handle_concurrency(error: ConcurrentModificationError) -> tuple[Response, int]:
        return jsonify({"error": error.code, "message": error.message}), 409

    @app.errorhandler(DomainValidationError)
    def handle_domain_logic(error: DomainValidationError) -> tuple[Response, int]:
        # أي خطأ في البزنس لم نصنفه تحديداً
        return jsonify({"error": "Domain Logic Error", "message": str(error)}), 400
