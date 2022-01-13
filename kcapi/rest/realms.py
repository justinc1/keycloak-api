from .crud import KeycloakCRUD
from .helper import ValidateParams


class KeycloakCaches: 
    def __init__(self, kcrud, realmName):
        self.name = realmName 
        self.request_body = {'realm': self.name}
        self.kcrud = kcrud  

    def postTo(self, target):
        return self.kcrud.append([self.name, target]).create(self.request_body)

    def clearUserCache(self):
        return self.postTo('clear-realm-cache')

    def clearRealmCache(self): 
        return self.postTo('clear-user-cache')

    def clearKeyCache(self):
        return self.postTo('clear-keys-cache')

class Realms(KeycloakCRUD):
    def __init__(self, url, token): 
        super().__init__(url, token)
        self.removeLast()

    def caches(self, realmName): 
        return KeycloakCaches(self, realmName)
