from .development import *
from os import environ

SECRET_KEY = environ.get("SECRET_KEY")
MONGO_URI = environ.get("DATABASE_URL")
DEBUG = environ.get("DEBUG")
ENV = environ.get("ENV")
