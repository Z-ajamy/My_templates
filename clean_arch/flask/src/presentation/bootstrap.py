from flasgger import Swagger
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.infrastructure.database.sqlalchemy_models.base import Base
from src.presentation.api.error_handler import register_error_handlers
from src.presentation.api.routes.user_routes import user_bp

from src.presentation.api.middlewares.request_tracker import setup_request_tracker

def create_app(db_url: str) -> Flask:
    app = Flask(__name__)

    swagger = Swagger(
        app,
        template={
            "info": {
                "title": "Clean Architecture Flask API",
                "description": "User Management Microservice API Documentation",
                "version": "1.0.0",
            }
        },
    )

    if db_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
        if db_url == "sqlite:///:memory:":
            engine = create_engine(
                db_url,
                connect_args=connect_args,
                poolclass=StaticPool,  # يضمن بقاء اتصال واحد حي دائماً
                echo=False,
            )
        else:
            # إذا كانت ملف (مثل sqlite:///dev.db)
            engine = create_engine(db_url, connect_args=connect_args, echo=False)
    else:
        # لمحركات الإنتاج (PostgreSQL, MySQL) لا نحتاج هذه التعديلات
        engine = create_engine(db_url, echo=False)

    Base.metadata.create_all(engine)

    # singilton factory
    app.config["SESS_MKR"] = sessionmaker(bind=engine, autoflush=False)

    app.register_blueprint(user_bp)

    register_error_handlers(app)

    setup_request_tracker(app)

    return app
