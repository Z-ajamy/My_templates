from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.infrastructure.database.sqlalchemy_models.base import Base
from src.presentation.api.routes.user_routes import user_bp
from src.presentation.api.error_handler import register_error_handlers

def create_app(db_url:str) -> Flask:
    app = Flask(__name__)

    engine = create_engine(db_url, echo=False)
    Base.metadata.create_all(engine)

    #singilton factory
    app.config["SESS_MKR"] = sessionmaker(bind=engine, autoflush=False)


    app.register_blueprint(user_bp)
    
    register_error_handlers(app)

    return app
