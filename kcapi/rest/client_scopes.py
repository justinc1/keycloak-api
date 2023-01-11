from .targets import Targets
from .crud import KeycloakCRUD


class ClientScopeCRUD(KeycloakCRUD):
    # GET /{realm}/client-scopes
    pass
    # def create(self, payload):
    #     # "composites" are setup via separated API
    #     # payload.pop("composites", None)
    #
    #     ret = super().create(payload)
    #     if "attributes" in payload:
    #         role = self.findFirstByKV("name", payload["name"])
    #         self.update(role["id"], payload).isOk()
    #     return ret


class ClientScopeScopeMappingsCRUD(KeycloakCRUD):
    # GET /{realm}/client-scopes/{id}/scope-mappings
    def create(self, payload):
        raise NotImplementedError()

    def update(self, obj_id=None, payload=None):
        raise NotImplementedError()

    def remove(self, _id, payload=None):
        raise NotImplementedError()


class ClientScopeScopeMappingsRealmCRUD(KeycloakCRUD):
    # GET /{realm}/client-scopes/{id}/scope-mappings/realm
    pass


class ClientScopeScopeMappingsClientCRUD(KeycloakCRUD):
    # GET /{realm}/client-scopes/{id}/scope-mappings/clients/{client} , {client} is client.id
    pass
