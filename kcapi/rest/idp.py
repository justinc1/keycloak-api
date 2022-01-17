from .crud import KeycloakCRUD

class IdentityProvider(KeycloakCRUD):
    RESOURCE = 'identity-provider/instances'

    @staticmethod
    def supportedResources(resource): 
        if resource in ['idp', 'identity-provider']: 
            return True
        else:
            return False

    @staticmethod
    def build(url, realm,  token): 
        idp = IdentityProvider(str(url), token) 
        
        idp.addResources(['auth','admin', 'realms'])
        idp.addResources([realm, IdentityProvider.RESOURCE])
        return idp




