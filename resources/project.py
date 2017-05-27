from common.services.projects import ProjectService
from common.filters.projects import ProjectFilter
from bson.objectid import ObjectId
from flask_restful import Resource
from common.utils.decorators import is_admindecorator
from common.models.project import ProjectModelView,Project
from flask import request
from flask_jwt_extended import get_jwt_identity,jwt_required
from common.exceptions.project import ProjectAddError,ProjectNotFoundError
from common.exceptions.sensors import SensorNotFoundError
from resources.schemas.project import AddProjectRequest

import datetime

class GetandAddProjectsForUser(Resource):

    decorators = [jwt_required]

    def __init__(self, **kwargs):
        self.database = kwargs["database"]


    def get(self):
        user_id = get_jwt_identity()
        if not ObjectId.is_valid(user_id):
            return {"message" : "Invalid user id"},500
        filter = ProjectFilter(id=user_id)
        rawProjects = ProjectService(self.database).find(filter=filter)
        if not rawProjects:
            return {"projects" : []},200
        projectsList = ProjectModelView().dump(rawProjects,many=True)
        return {"projects" : projectsList[0]},200

    def post(self):
        user_id = get_jwt_identity()
        validate = AddProjectRequest().validate(request.json)
        print(validate)
        if validate:
            return validate, 500
        if not ObjectId.is_valid(user_id):
            return {"message": "Invalid user id"}, 500
        args = request.json
        service = ProjectService(self.database)
        #Controllo che l'utente non abbia più di 25 progetti
        filter = ProjectFilter(id=user_id)
        n_progetti = len(service.find(filter=filter))
        print("Progetti: ",n_progetti)
        if n_progetti >= 25:
            return {"message" : "Too projects"},400
        newproject = Project(name=args["name"],description=args["description"],createdAt=datetime.datetime.now())
        try:
             service.add(project=newproject,userid=user_id)
        except ProjectAddError as e:
            return {"message" : str(e)},500
        except SensorNotFoundError as e:
            pass
        return {"message" : "Project added for user {0}".format(user_id)}





class GetProjectsAdminAndDelete(Resource):

    decorators = [jwt_required]


    def __init__(self, **kwargs):
        self.database = kwargs["database"]

    @is_admindecorator
    def get(self,id):
        if not ObjectId.is_valid(id):
            return {"message" : "Invalid user id"},500
        filter = ProjectFilter(id=id)
        rawProjects = ProjectService(self.database).find(filter=filter)
        if not rawProjects:
            return {"projects": []}, 200
        projectsList = ProjectModelView().dump(obj=rawProjects, many=True)
        return {"projects": projectsList[0]}, 200

    def delete(self,id):
        if not ObjectId.is_valid(id):
            return {"message" : "Invalid project id"},500
        user_id = get_jwt_identity()
        if not ObjectId.is_valid(user_id):
            return {"message" : "Invalid user id"},500
        service = ProjectService(self.database)
        print(id,user_id)
        try:
            service.delete(projectid=id,userid=user_id)
        except ProjectNotFoundError as e:
            return {"message" : str(e)},500
        except SensorNotFoundError as e:
            pass
        return 400



