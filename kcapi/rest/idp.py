from .crud import KeycloakCRUD

class IdentityProvider(KeycloakCRUD):
    def __init__(self, url, token, custom_targets = {}): 
        super().__init__(url, token, custom_targets)
        self.removeLast()
        self.addResources(['identity-provider' , 'instances'])




