from flask import Flask
from flask_pymongo import PyMongo

mongo = PyMongo()


def create_app(development_settings=None, production_settings=None):
    app = Flask(__name__)
    app.config.from_object(development_settings)
    app.config.from_object(production_settings)

    mongo.init_app(app)

    with app.app_context():
        from . import routes
        from .api import api_bp

        app.register_blueprint(api_bp, url_prefix="/api")

        return app
