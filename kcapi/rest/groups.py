from .crud import KeycloakCRUD
from .helper import ValidateParams
from .resp import ResponseHandler
import json, requests


class RealmsRolesMapping(KeycloakCRUD): 
    def __init__(self, url, token, custom_targets = None): 
        super().__init__(url, token, custom_targets)

        self.rolesAPI = KeycloakCRUD(token = token, KeycloakAPI=self)
        self.rolesAPI.changeTarget('roles')


    def setGroup(self, groupObject):
        groupID = self.findFirst(groupObject)['id']
        self.addResources([groupID, 'role-mappings', 'realm'])
        return self

    def __fetchRoles(self, roles): 
        find = self.rolesAPI.findFirstByKV
        return list( map(lambda name: find('name', name), roles) )



    def add(self, roles): 
        populatedListOfRoles = self.__fetchRoles(roles)
        return self.create(populatedListOfRoles)

    # Another example of Keycloak not using standard REST behaviour.
    def remove(self, roles): 
        populatedListOfRoles = self.__fetchRoles(roles)
        remove_target = self._KeycloakCRUD__targets['delete']

        ret = requests.delete(remove_target, data=json.dumps(populatedListOfRoles), headers=self.getHeaders() )
        return ResponseHandler(remove_target).handleResponse(ret)
        

     


class Groups(KeycloakCRUD): 
    def __init__(self, url, token): 
        super().__init__(url, token)
        self.realmRolesAPI = RealmsRolesMapping(url, token)

    def realmRoles(self, group):
        return self.realmRolesAPI.setGroup(group)

    def removeRealmRoles(self, group, roles):
        groupID = super().findFirst(group)['id']
        roleMap = map(self.__getRole, roles) 

        realmRolesAPI = self.extend([groupID, 'role-mappings', 'realm'])

        ret = self._KeycloakCRUD__req().delete(str(target_url), data=json.dumps(list(roleMap)), headers=self.getHeaders() )
        return ret


