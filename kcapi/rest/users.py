from .crud import KeycloakCRUD
from .helper import ValidateParams


class Users(KeycloakCRUD):
    def __init__(self, url, token, custom_targets = None): 
        super().__init__(url, token, custom_targets)

        groupsAPI = KeycloakCRUD(token = token, KeycloakAPI=self)
        groupsAPI.changeTarget('groups')
        self.findGrp = groupsAPI.findFirst

        


    def __userGroupMappingAPI(self, userID): 
        kc = KeycloakCRUD(None, self.token, KeycloakAPI = self) 
        kc.addResources([userID, 'groups'])
        return kc

    def joinGroup(self, user, group): 
        userID = self.findFirst(user)['id']
        groupID = self.findGrp(group)['id']

        requestBody = {'groupId': groupID, 'userId': userID} 

        return self.__userGroupMappingAPI(userID).update(groupID, requestBody)

    def groups(self, user):
        userID = super().findFirst(user)['id']
        return self.__userGroupMappingAPI(userID).all()

    def leaveGroup(self, user, group):
        userID  = super().findFirst(user)['id']
        groupID = self.findGrp(group)['id']

        return self.__userGroupMappingAPI(userID).remove(groupID)

    # 
    # credentials: {type: "password", value: "passphrases", temporary: true} 
    # type: **password** Is the credential type supported by Keycloak.
    # value: Here we put the passphrase (required) 
    # temporary: **true** Means that this password would works the first time but it will force the user to setup a new one. 
    def updateCredentials(self, user, credentials):

        params = {"type": "password", "temporary":True}
        userID = super().findFirst(user)['id']
        
        params.update(credentials)
        ValidateParams(['type', 'value', 'temporary'],params)
        
        credentials = KeycloakCRUD(token = self.token, KeycloakAPI=self)
        credentials.addResources([userID, 'reset-password'])

        return credentials.update('', params)


