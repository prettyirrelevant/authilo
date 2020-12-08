from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo

mongo = PyMongo()
cors = CORS()


def create_app(development_settings=None, production_settings=None):
    app = Flask(__name__)
    app.config.from_object(development_settings)
    app.config.from_object(production_settings)

    cors.init_app(app)
    mongo.init_app(app)

    with app.app_context():
        from . import routes
        from .api import api_bp

        app.register_blueprint(api_bp, url_prefix="/api")

        return app
