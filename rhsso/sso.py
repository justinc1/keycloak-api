import requests, json
from .url import RestURL
from .crud import KeycloakCRUD
from .oid import OpenID
from .patches import Roles, Users
from .relational import UserAndGroupRelation

#sso-cvaldezr-dev.apps.sandbox.x8i5.p1.openshiftapps.com

DEBUG = False

factory = {"roles": Roles, "users": Users}

class KeycloakAdmin: 
    def __init__(self, conf, url):
        self.client_conf = {
                "client_id": "admin-cli",
                "grant_type":"password",
                "realm" : "master"
        }

        self.client_conf['username'] = conf['username']
        self.client_conf['password'] = conf['password']

        self.oidc = OpenID(self.client_conf, RestURL(url=url))
        self.restURL = RestURL(url=url, resources=["auth", "admin"])

    def __call(self, endpointURL):
        token = self.oidc.getToken(endpointURL.target())
        API = KeycloakCRUD(str(endpointURL), token)

        if API.findAll().isOk(): 
            return API
        else:
            raise Exception("Keycloak resource: " + str(self.restURL))
            return None

    def master(self):
        endpoint = self.restURL.copy() 
        endpoint.addResources(["realms"])
        return self.__call(endpoint) 

    def buildRealmAPI(self, resourceName, realm):
        endpoint = self.restURL.copy() 
        endpoint.addResources(["realms", realm, resourceName])
        return self.__call(endpoint) 

    def buildForURL(self, restURLObject): 
        return self.__call(restURLObject) 

class Keycloak: 
    def __init__(self, token, url):
        if not token: 
            raise Exception("No authentication token provided.")
        if not url: 
            raise Exception("No Keycloak endpoint URL has been provided.")

        self.token = token 
        self.restURL = RestURL(url=url, resources=["auth", "admin"])

    def __call(self, endpointURL):
        API = KeycloakCRUD(str(endpointURL), self.token)

        return API

    def __create(self, endpoint, resourceName): 
        ResourceAPI = KeycloakCRUD if not resourceName in factory else factory[resourceName]  
        return ResourceAPI(str(endpoint), self.token)

    
    def admin(self):
        endpoint = self.restURL.copy() 
        endpoint.addResources(["realms"])
        return self.__call(endpoint) 

    def build(self, resourceName, realm):
        endpoint = self.restURL.copy() 
        endpoint.addResources(["realms", realm, resourceName])
        return self.__create(endpoint, resourceName) 

    def group_joining_api(self, realm): 
        endpoint = self.restURL.copy() 
        users = self.build('users', realm)
        groups = self.build('groups', realm)
        endpoint.addResources(["realms", realm])
        return UserAndGroupRelation(users, groups, endpoint)


    
