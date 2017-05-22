from common.settings import persistenceSettings,authSettings
from untitled import flask_bcrypt
from common.services.userservice import UserService
from common.filters.users import UserFilter
from flask.ext.jwt_extended import revoke_token

class AuthManager:
    def __init__(self,database):
        self.users = database

    def login(self,username,password):
        """
        Questo metodo effettua il login dell'utente controllando le sue credenziali.
        :param username: Username utente
        :param password: Password utente
        :return: id utente loggato / False
        """
        service = UserService(self.users)
        loginfilter = UserFilter(username=username)
        user = service.find(loginfilter)[0]
        #Check password
        if flask_bcrypt.check_password_hash(pw_hash=user.password,password=password):
            #Login effettuato
            return user.id
        return False


    def logout(self,token):
        """
        Metodo per il logout di un utente, inserisce nella blacklist,ovvero la lista di token non più usabili
        quello passato in input.
        :param token: User jwt token
        :return: True/False
        """
        try:
            jti = token['jti']
            revoke_token(jti)
        except KeyError:
            return False
        return True


    def register(self,username,password,email):
        """
        Metodo per registrare un nuovo utente.
        :param username: Username utente
        :param password: Password utente
        :param email: email utente
        :return: id dell'utente registrato / False
        """

