from datetime import datetime

from flask import request, json
from flask_restful import Resource, reqparse
from werkzeug.security import generate_password_hash, check_password_hash
from bson.json_util import dumps
from . import api
from .. import mongo


class Register(Resource):
    def post(self):
        # parse request data
        parser = reqparse.RequestParser()
        parser.add_argument("password", type=str, required=True)

        # check if API-Key is present in the header
        if not request.headers.get("X-Api-Key"):
            return {"message": "API Key not provided"}, 400

        # check if API-Key is present in DB
        project = mongo.db.projects.find_one(
            {"api_key": request.headers.get("X-Api-Key")}
        )

        # check if API-Key length is up to 32 characters
        if len(request.headers.get("X-Api-Key")) != 32 or not project:
            return {"message": "API Key is invalid"}, 400

        # add parser argument based on project method of authentication
        if project["method_of_auth"] == "email":
            parser.add_argument("email", type=str, required=True)

        if project["method_of_auth"] == "username":
            parser.add_argument("username", type=str, required=True)

        # check if the required args are present
        parser.parse_args()

        data = json.loads(request.data)

        # checks if username/email exists
        if project["method_of_auth"] == "username":
            if mongo.db.accounts.find_one({"username": data.get("username")}):
                return {"message": "Username already exists!"}, 400

        if project["method_of_auth"] == "email":
            if mongo.db.accounts.find_one({"email": data.get("email")}):
                return {"message": "Email already exists!"}, 400

        data.update(
            {
                "project_id": project["_id"],
                "password": generate_password_hash(data.get("password")),
                "created_at": datetime.now(),
            }
        )

        new_account = mongo.db.accounts.insert_one(data)

        return {"message": "Account created successfully!"}, 201


class Login(Resource):
    def post(self):
        # parse request data
        parser = reqparse.RequestParser()
        parser.add_argument("password", type=str, required=True)

        # check if API-Key is present in the header
        if not request.headers.get("X-Api-Key"):
            return {"message": "API Key not provided"}, 400

        # check if API-Key is present in DB
        project = mongo.db.projects.find_one(
            {"api_key": request.headers.get("X-Api-Key")}
        )

        # check if API-Key length is up to 32 characters
        if len(request.headers.get("X-Api-Key")) != 32 or not project:
            return {"message": "API Key is invalid"}, 400

        # add parser argument based on project method of authentication
        if project["method_of_auth"] == "email":
            parser.add_argument("email", type=str, required=True)

        if project["method_of_auth"] == "username":
            parser.add_argument("username", type=str, required=True)

        # check if the required args are present
        parser.parse_args()

        data = json.loads(request.data)
        account = None

        # validate data
        if project["method_of_auth"] == "username":
            account = mongo.db.accounts.find_one({"username": data.get("username")})
            if not account and check_password_hash(
                account.get("password", ""), data["password"]
            ):
                return {"message": "Username and/or password mismatch!"}, 400

        if project["method_of_auth"] == "email":
            account = mongo.db.accounts.find_one({"email": data.get("email")})
            if not account and check_password_hash(
                account.get("password", ""), data["password"]
            ):
                return {"message": "Email and/or password mismatch!"}, 400

        #  a little cleaning here and there
        account.pop("password")
        account.pop("project_id")

        return json.loads(dumps(account)), 200


api.add_resource(Register, "/register")
api.add_resource(Login, "/login")
