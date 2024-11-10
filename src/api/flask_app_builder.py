from typing import List

from flask import Flask, Blueprint
from flask_wtf.csrf import CSRFProtect


class FlaskAppBuilder:
    def __init__(self) -> None:
        self._app = Flask(__name__)
    
    def with_config(self, config: dict):
        self._app.config.update(config)
        return self
    
    def with_csrf_protection(self):
        if not self._app.config.get("SECRET_KEY"):
            raise ValueError("A SECRET_KEY must be set before initializing CSRF protection.")
        csrf = CSRFProtect()
        csrf.init_app(self._app)
        return self
    
    def with_blueprints(self, blueprints: Blueprint | List[Blueprint]):
        if isinstance(blueprints, Blueprint):
            self._app.register_blueprint(blueprints)
        else:
            for blueprint in blueprints:
                self._app.register_blueprint(blueprint)
        return self
    
    def build(self) -> Flask:
        return self._app