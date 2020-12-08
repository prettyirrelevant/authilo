from flask import Flask
from flask_pymongo import PyMongo

mongo = PyMongo()


def create_app(settings=None):
    app = Flask(__name__)
    app.config.from_object(settings)

    mongo.init_app(app)

    with app.app_context():
        from . import routes
        from .api import api_bp

        app.register_blueprint(api_bp, url_prefix='/api')

        return app
