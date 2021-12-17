from .crud import KeycloakCRUD
from .helper import ValidateParams


class Users(KeycloakCRUD):
    def joingroup(self, user, group): 
        userid = super().findfirst(user)['id']
        groupid = super().buildnew('groups').findfirst(group)['id']
        
        reqbody = {'groupid': groupid, 'userid': userid} 
        return super().extend([userid, 'groups']).update(groupid, reqbody)

    def groups(self, user):
        userID = super().findFirst(user)['id']
        return super().extend([userID, 'groups']).findAll().verify().resp().json()

    def leaveGroup(self, user, group):
        userID = super().findFirst(user)['id']
        groupID = super().buildNew('groups').findFirst(group)['id']

        return super().extend([userID, 'groups']).remove(groupID)

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

        return super().extend([userID, 'reset-password']).update('', params)


