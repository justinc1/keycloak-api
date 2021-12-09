from .crud import KeycloakCRUD
from .helper import ValidateParams
import json

class Groups(KeycloakCRUD): 
    def __init__(self, url, token): 
        super().__init__(url, token)

    def __getRole(self, roleName): 
        return self.buildNew('roles').findFirstByKV('name', roleName)

    def addRealmRoles(self, group, roles):
        groupID = self.findFirst(group)['id']
        roleMap = map(self.__getRole, roles) 

        return self.extend([groupID, 'role-mappings', 'realm']).create(list(roleMap))

    def getRealmRoles(self, group):
        groupID = self.findFirstByKV(group['key'], group['value'])['id']
        return self.extend([groupID, 'role-mappings', 'realm']).findAll().verify().resp().json()

    def removeRealmRoles(self, group, roles):
        groupID = super().findFirst(group)['id']
        roleMap = map(self.__getRole, roles) 

        target_url = self.extend([groupID, 'role-mappings', 'realm']).getURL()
        ret = self._KeycloakCRUD__req().delete(str(target_url), data=json.dumps(list(roleMap)), headers=self.getHeaders() )
        return ret


