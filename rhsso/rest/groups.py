from .crud import KeycloakCRUD
from .helper import ValidateParams

class Groups(KeycloakCRUD): 
    def __getRole(self, roleName): 
        return super().buildNew('roles').findFirstByKV('name', roleName)

    def addRealmRoles(self, group, roles):
        groupID = super().findFirst(group)['id']
        roleMap = map(self.__getRole, roles) 

        return super().extend([groupID, 'role-mappings', 'realm']).create(list(roleMap))

    def getRealmRoles(self, group):
        groupID = super().findFirstByKV(group['key'], group['value'])['id']
        return super().extend([groupID, 'role-mappings', 'realm']).findAll().verify().resp().json()
