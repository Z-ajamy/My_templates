# the entry point of app

from src.presentation.bootstrap import create_app
from src.presentation.config import settings

if __name__ == "__main__":
    app = create_app(db_url=settings.database_url)
    app.run(host="0.0.0.0", port=5000, debug=settings.flask_debug)

