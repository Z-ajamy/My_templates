import uuid

from flask import Flask, Response, request

from src.infrastructure.logger.setup import app_logger


def setup_request_tracker(app: Flask) -> None:
    @app.before_request
    def assign_request_id() -> None:
        req_id = request.headers.get("X-Request-ID")
        if not req_id:
            req_id = str(uuid.uuid4())

        request.request_id = req_id

        app_logger.info(f"Incoming Request: {request.method} {request.path}")

    @app.after_request
    def attach_request_id_to_response(response: Response) -> Response:
        app_logger.info(f"Outgoing Response: {response.status_code}")

        if hasattr(request, "request_id"):
            response.headers["X-Request-ID"] = request.request_id

        return response
