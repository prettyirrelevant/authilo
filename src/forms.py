from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators, SelectField

from . import mongo


class RegisterForm(FlaskForm):
    username = StringField(
        "username",
        validators=[
            validators.DataRequired(),
            validators.Length(min=4, max=20),
            validators.Regexp(
                "^[a-zA-Z0-9_]+$", message="Only alphanumeric characters are allowed"
            ),
        ],
    )
    password = PasswordField(
        "password",
        validators=[validators.Length(min=8, max=30), validators.DataRequired()],
    )
    confirm_password = PasswordField(
        "confirm_password",
        validators=[
            validators.EqualTo("password", message="Passwords don't match"),
            validators.DataRequired(),
        ],
    )

    def validate_username(self, username):
        user = mongo.db.users.find_one({"username": username.data})
        if user:
            raise validators.ValidationError("username is not available")


class LoginForm(FlaskForm):
    username = StringField(
        "username",
        validators=[validators.DataRequired(), validators.Length(min=4, max=20)],
    )
    password = PasswordField(
        "password",
        validators=[validators.Length(min=8, max=30), validators.DataRequired()],
    )


class ProjectForm(FlaskForm):
    project_name = StringField("Project name", validators=[validators.DataRequired()])
    method_of_authentication = SelectField(
        "Method of Authentication",
        choices=[("email", "Email Address"), ("username", "Username")],
        validators=[validators.DataRequired()],
    )
