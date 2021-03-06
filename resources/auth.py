from flask_restful import fields, marshal_with, reqparse, Resource,HTTPException
from flask_jwt_extended import create_access_token,jwt_required,get_raw_jwt
from resources.schemas.auth import LoginRequest
from flask import request
import logging


class AuthLogin(Resource):
    def __init__(self,**kwargs):
        self.authManager = kwargs["auth_manager"]

    def post(self):
        validation =  LoginRequest().validate(request.json)
        #TODO ADD DECORATOR FOR THIS
        if validation:
            return validation,500
        username = request.json["username"]
        password = request.json["password"]
        result,role = self.authManager.login(username,password)
        if result:
            token = create_access_token(identity=result)
            return {"accessToken" : token, "role" : role},200
        return {"message" : "INVALID CREDENTIALS"},401



class AuthLogout(Resource):
    decorators = [jwt_required]
    def __init__(self,**kwargs):
        self.authManager = kwargs["auth_manager"]

    def post(self):
        try:
            self.authManager.logout(get_raw_jwt())
        except KeyError:
           return {"message" : "Invalid token"},500
        return {"message" : "Successfully logout"},200






