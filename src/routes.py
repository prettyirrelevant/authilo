import uuid
from datetime import datetime

from bson import ObjectId
from flask import (
    current_app as app,
    render_template,
    session,
    redirect,
    url_for,
    flash,
    request,
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_parse

from . import mongo
from .forms import RegisterForm, LoginForm, ProjectForm
from .utils import login_required, generate_project_avatar


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    user = mongo.db.users.find_one({"username": session.get("username")})
    if user:
        return redirect(url_for("projects"))

    form = RegisterForm()

    if form.validate_on_submit():
        user = mongo.db.users.insert_one(
            {
                "username": form.username.data,
                "avatar_url": f"https://avatars.dicebear.com/api/bottts/{form.username.data}.svg",
                "password": generate_password_hash(form.password.data),
                "created_at": datetime.now(),
            }
        )
        flash("Your account creation was successful", "green")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register | AuthiLo", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    user = mongo.db.users.find_one({"username": session.get("username")})
    if user:
        return redirect(url_for("projects"))

    form = LoginForm()
    if form.validate_on_submit():
        user = mongo.db.users.find_one({"username": form.username.data})
        if user and check_password_hash(user["password"], form.password.data):
            session["username"] = user["username"]
            flash("Login successful", "green")

            next_page = request.args.get("next")
            print(next_page)
            if not next_page or url_parse(next_page).netloc != "":
                next_page = url_for("projects")
            return redirect(next_page)

        flash("Username and/or password mismatch", "red")
    return render_template("login.html", title="Login | AuthiLo", form=form)


@app.route("/projects")
@login_required
def projects():
    form = ProjectForm()
    user = mongo.db.users.find_one({"username": session.get("username")})
    user_projects = mongo.db.projects.find({"user_id": user["_id"]})
    return render_template(
        "projects.html",
        title="Resources | AuthiLo",
        user_projects=list(user_projects),
        form=form,
    )


@app.route("/project/<id>")
@login_required
def project(id):
    _project = mongo.db.projects.find_one({"_id": ObjectId(id)})
    project_accounts = mongo.db.accounts.find({"project_id": ObjectId(_project["_id"])})
    return render_template(
        "project.html",
        title="Project | AuthiLo",
        project=_project,
        project_accounts=list(project_accounts),
    )


@app.route("/project/<id>/delete")
@login_required
def delete_project(id):
    user = mongo.db.users.find_one({"username": session.get("username")})
    _project = mongo.db.projects.find_one({"_id": ObjectId(id), "user_id": user["_id"]})
    if not _project:
        flash("Sorry you don't have such project", "yellow")
        return redirect(url_for("projects"))

    mongo.db.accounts.delete_many({"project_id": _project["_id"]})
    mongo.db.projects.delete_one({"_id": ObjectId(id), "user_id": user["_id"]})
    flash("Project deleted successfully", "green")
    return redirect(url_for("projects"))


@app.route("/add_project", methods=["POST"])
@login_required
def add_project():
    form = ProjectForm(request.form)
    if form.validate_on_submit():
        user = mongo.db.users.find_one({"username": session.get("username")})
        new_project = mongo.db.projects.insert_one(
            {
                "user_id": user["_id"],
                "name": form.project_name.data,
                "method_of_auth": form.method_of_authentication.data,
                "url": generate_project_avatar(form.project_name.data),
                "api_key": uuid.uuid4().hex,
                "created_at": datetime.now(),
            }
        )
        flash("Project created successfully", "green")
        return redirect(url_for("projects"))

    return redirect(url_for("projects"))


@app.route("/delete_account")
@login_required
def delete_account():
    user = mongo.db.users.find_one({"username": session.get("username")})
    for _project in mongo.db.projects.find({"user_id": user["_id"]}):
        mongo.db.accounts.delete_many({"project_id": _project["_id"]})

    mongo.db.projects.delete_many({"user_id": user["_id"]})
    mongo.db.users.delete_one({"username": session.get("username")})
    session.pop("username")

    flash("Account deletion was succussful", "green")
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.pop("username")
    flash("Logged out successfully", "green")
    return redirect(url_for("index"))
