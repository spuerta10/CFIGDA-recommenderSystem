import os
from secrets import token_hex

from flask import Flask

from api.flask_app_builder import FlaskAppBuilder
from api.controller.controller import controller_bp


def create_app() -> Flask:
    config = {
        "SECRET_KEY": os.environ.get("SECRET_KEY", f"{token_hex(32)}"),
        "WTF_CSRF_ENABLED": True  
    }
    app = FlaskAppBuilder() \
        .with_config(config) \
        .with_blueprints(controller_bp) \
        .with_csrf_protection() \
        .build()
    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 9092)))
