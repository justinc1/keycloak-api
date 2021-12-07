from .crud import KeycloakCRUD
from .helper import ValidateParams
import requests

# Patching Roles service to patch delete roles behaviour on Keycloak.
class Roles(KeycloakCRUD):
    def remove(self, _id): 
        self.resource_url.replaceResource('roles', 'roles-by-id')
        resp = super().remove(_id)
        self.resource_url.replaceResource('roles-by-id', 'roles')
        return resp

class Users(KeycloakCRUD):
    def joinGroup(self, user, group): 
        user_obj = super().findFirstByKV(user['key'], user['value'])
        group_obj = super().buildNew('groups').findFirstByKV(group['key'], group['value'])

        user_id = user_obj['id']
        group_id = group_obj['id']
        payload ={'groupId': group_id, 
                'userId': user_id} 

        return super().extend([user_id, 'groups']).update(group_id, payload)

    def groups(self, user):
        user_id = super().findFirstByKV(user['key'], user['value'])['id']
        return super().extend([user_id, 'groups']).findAll().verify().resp().json()

    def leaveGroup(self, user, group):
        user_obj = super().findFirstByKV(user['key'], user['value'])
        group_obj = super().buildNew('groups').findFirstByKV(group['key'], group['value'])

        user_id = user_obj['id']
        group_id = group_obj['id']

        return super().extend([user_id, 'groups']).remove(group_id)

    # 
    # credentials: {type: "password", value: "passphrases", temporary: true} 
    # type: **password** Is the credential type supported by Keycloak.
    # value: Here we put the passphrase (required) 
    # temporary: **true** Means that this password would works the first time but it will force the user to setup a new one. 
    def updateCredentials(self, user, credentials):

        params = {"type": "password", "temporary":True}
        user_id = super().findFirstByKV(user['key'], user['value'])['id']
        
        params.update(credentials)
        ValidateParams(['type', 'value', 'temporary'],params)

        return super().extend([user_id, 'reset-password']).update('', params)


