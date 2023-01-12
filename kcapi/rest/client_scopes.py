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

    def scope_mappings_api(self, *, client_scope_id):
        scope_mappings_api = ClientScopeScopeMappingsCRUD.get_child(self, client_scope_id, "scope-mappings")
        return scope_mappings_api

    def protocol_mapper_api(self, *, client_scope_id):
        protocol_mapper_api = ClientScopeProtocolMapperCRUD.get_child(self, client_scope_id, "protocol-mappers/models")
        return protocol_mapper_api

    def scope_mappings_realm_api(self, *, client_scope_id):
        scope_mappings_api = self.scope_mappings_api(client_scope_id=client_scope_id)
        scope_mappings_realm_api = ClientScopeScopeMappingsRealmCRUD.get_child(scope_mappings_api, None, "realm")
        return scope_mappings_realm_api

    # def scope_mappings_clients_api(self, *, client_scope_id, client_id):
    #     scope_mappings_api = self.scope_mappings_api(client_scope_id=client_scope_id)
    #     scope_mappings_clients_api = scope_mappings_api.get_child(ClientScopeScopeMappingsClientsCRUD, "clients", client_id)
    #     return scope_mappings_clients_api


class ClientScopeScopeMappingsCRUD(KeycloakCRUD):
    # GET /{realm}/client-scopes/{id}/scope-mappings
    def create(self, payload):
        raise NotImplementedError()

    def update(self, obj_id=None, payload=None):
        raise NotImplementedError()

    def remove(self, _id, payload=None):
        raise NotImplementedError()


class ClientScopeProtocolMapperCRUD(KeycloakCRUD):
    # GET /{realm}/client-scopes/{id}/protocol-mappers/models
    pass


class ClientScopeScopeMappingsRealmCRUD(KeycloakCRUD):
    # GET /{realm}/client-scopes/{id}/scope-mappings/realm
    def update(self, obj_id=None, payload=None):
        raise NotImplementedError()


class ClientScopeScopeMappingsClientCRUD(KeycloakCRUD):
    # GET /{realm}/client-scopes/{id}/scope-mappings/clients/{client} , {client} is client.id
    pass
