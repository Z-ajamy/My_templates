# the entry point of app

from src.presentation.bootstrap import create_app
from src.presentation.config import settings

app = create_app(db_url=settings.database_url)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=settings.flask_debug)
