from typing import List

from flask import Flask, Blueprint
from flask_wtf.csrf import CSRFProtect


class FlaskAppBuilder:
    """
    A builder class for creating and configuring a Flask application.

    This class provides a fluent interface for adding configurations,
    CSRF protection, blueprints, and other components to a Flask application.
    """
    def __init__(self) -> None:
        """
        Initializes a new instance of the FlaskAppBuilder.

        Creates an internal Flask application instance that can be configured
        using the provided builder methods.
        """
        self._app = Flask(__name__)

    def with_config(self, config: dict):
        """
        Updates the application configuration.

        Args:
            config (dict): A dictionary containing configuration key-value pairs.

        Returns:
            FlaskAppBuilder: The current instance, allowing method chaining.
        """
        self._app.config.update(config)
        return self

    def with_csrf_protection(self):
        """
        Enables CSRF protection for the application.

        Raises:
            ValueError: If the "SECRET_KEY" is not set in the application configuration.

        Returns:
            FlaskAppBuilder: The current instance, allowing method chaining.
        """
        if not self._app.config.get("SECRET_KEY"):
            raise ValueError(
                "A SECRET_KEY must be set before initializing CSRF protection."
            )
        csrf = CSRFProtect()
        csrf.init_app(self._app)
        return self

    def with_blueprints(self, blueprints: Blueprint | List[Blueprint]):
        """
        Registers one or more blueprints with the application.

        Args:
            blueprints (Blueprint | List[Blueprint]): A single Flask Blueprint or a
                list of Flask Blueprints to register with the application.

        Returns:
            FlaskAppBuilder: The current instance, allowing method chaining.
        """
        if isinstance(blueprints, Blueprint):
            self._app.register_blueprint(blueprints)
        else:
            for blueprint in blueprints:
                self._app.register_blueprint(blueprint)
        return self

    def build(self) -> Flask:
        """
        Builds and returns the configured Flask application instance.

        Returns:
            Flask: The configured Flask application.
        """
        return self._app
