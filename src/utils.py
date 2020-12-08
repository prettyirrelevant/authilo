import secrets
from functools import wraps

from flask import current_app as app, redirect, url_for, request, session, flash

from . import mongo


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('username') or not mongo.db.users.find_one({"username": session.get("username")}):
            flash("You need to be logged in to do that", "yellow")
            return redirect(url_for("login", next=get_url(request.url)))
        return f(*args, **kwargs)

    return decorated_function


@app.context_processor
def user_in_session():
    if session.get("username", None):
        user = mongo.db.users.find_one({"username": session.get("username")})
    else:
        user = None
    return dict(current_user=user)


def get_url(url):
    return "/" + url.split("/")[-1]


def generate_project_avatar(name):
    hexcode = secrets.token_hex()[:6]
    return f"https://avatar.oxro.io/avatar.svg?name={name}&background={hexcode}&length=1"
