from .crud import KeycloakCRUD
from .helper import ValidateParams

class Roles(KeycloakCRUD):

    # The Keycloak guys decided to use another resource DELETE /roles-by-id, instead of sticking to DELETE /roles.
    # which should be expected for /roles, the method remove override the default RESTful behaviour to make it work.
    def remove(self, _id): 
        self.resource_url.replaceResource('roles', 'roles-by-id')
        resp = super().remove(_id)
        self.resource_url.replaceResource('roles-by-id', 'roles')
        return resp


