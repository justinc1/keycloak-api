from .crud import KeycloakCRUD
from .groups import Groups
from .roles import Roles   
from .users import Users   
from .url import RestURL
from .auth_flows import AuthenticationFlows

KCResourceTypes = {
        "roles": Roles, 
        "users": Users, 
        "groups": Groups, 
        "authentication": AuthenticationFlows,
}

class KCResourceBuilder:
    def __URLSetup(self, url):
        return RestURL(url=url, resources=["auth", "admin", "realms"])
    
    def __init__(self, keycloakURL):
        self.name = None
        self.realm = None
        self.url = self.__URLSetup(keycloakURL) 

    def withName(self, name):
        self.name = name
        return self

    def forRealm(self, realm): 
        self.realm = realm
        return self

    def build(self, token):
        KCResourceAPI = KeycloakCRUD if not self.name in KCResourceTypes else KCResourceTypes[self.name]  

        self.url.addResources([self.realm, self.name])
        return KCResourceAPI(str(self.url), token) 

