from flask import Flask
from src.infrastructure.container import AppContainer
from src.presentation.api.routes.user_routes import user_bp
from src.presentation.api.error_handler import register_error_handlers
from src.presentation.api.middlewares.request_tracker import setup_request_tracker

def create_app(db_url: str) -> Flask:
    app = Flask(__name__)
    
    container = AppContainer()
    container.config.db_url.from_value(db_url)
    
    app.container = container
    
    setup_request_tracker(app)
    register_error_handlers(app)
    
    # 4. تسجيل المسارات
    app.register_blueprint(user_bp)
    
    return app
