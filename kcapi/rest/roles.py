from .crud import KeycloakCRUD
from .helper import ValidateParams



# The Keycloak guys decided to use another resource DELETE /roles-by-id, instead of sticking to DELETE /roles.
class Roles(KeycloakCRUD):
    def __init__(self, url, token, custom_targets = {}): 
        super().__init__(url, token, custom_targets)
        self._KeycloakCRUD__targets['delete'].replaceResource('roles', 'roles-by-id')



