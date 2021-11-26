from .crud import KeycloakCRUD

# Patching Roles service to patch delete roles behaviour on Keycloak.
class Roles(KeycloakCRUD):
    def remove(self, _id): 
        self.resource_url.replaceResource('roles', 'roles-by-id')
        resp = super().remove(_id)
        self.resource_url.replaceResource('roles-by-id', 'roles')
        return resp


