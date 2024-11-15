from api.flask_app_builder import FlaskAppBuilder

import pytest
from flask import Flask, Blueprint


@pytest.fixture
def flask_app_builder() -> FlaskAppBuilder:
    return FlaskAppBuilder()


def test_with_config(flask_app_builder: FlaskAppBuilder):
    config = {"DEBUG":True, "TESTING": True}
    builder = flask_app_builder.with_config(config)
    
    assert builder._app.config["DEBUG"] is True
    assert builder._app.config["TESTING"] is True

    
def test_with_csrf_protection_no_secret_key(flask_app_builder: FlaskAppBuilder):
    with pytest.raises(ValueError):
        flask_app_builder.with_csrf_protection()
        

def test_with_csrf_protection_with_secret_key(flask_app_builder: FlaskAppBuilder):
    app: Flask = flask_app_builder \
        .with_config({"SECRET_KEY": "test"}) \
        .with_csrf_protection().build()
    
    assert "csrf" in app.extensions
    
    from flask_wtf.csrf import CSRFProtect
    assert isinstance(app.extensions["csrf"], CSRFProtect)
    
    
def test_with_single_blueprint(flask_app_builder: FlaskAppBuilder): 
    blueprint = Blueprint("test_blueprint", __name__)
    
    app: Flask = flask_app_builder.with_blueprints(blueprint).build()
    
    assert "test_blueprint" in app.blueprints
    

def test_with_multiple_blueprints(flask_app_builder: FlaskAppBuilder): 
    blueprint1, blueprint2 = Blueprint("test_blueprint1", __name__), Blueprint("test_blueprint2", __name__)
    
    app: Flask = flask_app_builder.with_blueprints([blueprint1, blueprint2]).build() 
    
    assert "test_blueprint1" in app.blueprints
    assert "test_blueprint2" in app.blueprints
    

def test_build(flask_app_builder: FlaskAppBuilder):
    app = flask_app_builder.build()
    
    assert isinstance(app, Flask)