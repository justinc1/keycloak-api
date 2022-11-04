from .crud import KeycloakCRUD


class Role():
    def __init__(self, kc, role):
        self.value = role
        self.kc = kc

    def composite(self):
        return Composites(self.kc, self.value['id'])



class Composites():
    def __init__(self, kc, roleID):
        self.kc = kc
        self.id = roleID

        # It just adds few extra resource to the url: /id/composites
        self.post = lambda payload: KeycloakCRUD.derive(kc, ['roles-by-id' , self.id, 'composites']).create(payload)
        self.remove = lambda payload: KeycloakCRUD.derive(kc, ['roles-by-id', self.id, 'composites']).remove(payload)

        # It just adds few extra resource to the url: /id/composites/realm
        self.get = lambda: KeycloakCRUD.derive(kc,  ['roles-by-id' , self.id, 'composites', 'realm']).findAll()

        self.get_role_by_name = lambda name='': KeycloakCRUD.derive(kc, ['roles']).findFirstByKV(key='name', value=name)

    def link(self, roleName):
        role = self.get_role_by_name(roleName)

        if not role:
            raise("Error the role "+roleName+" not found!")

        return self.post([role])

    def unlink(self, roleName):
        role = self.get_role_by_name(roleName)

        if not role:
            raise ("Error the role " + roleName + " not found!")

        return self.remove(role['id'])
    def findAll(self):
        return self.get()


def hack_rest_roles_remove_endpoint(that, kc):
    custom_delete = that.targets.targets['delete'].copy()
    custom_delete.replaceResource('clients', 'roles-by-id')
    kc.targets.targets['delete'] = custom_delete

    return kc

def new_child(kc, query, child_resource):
    client_id = kc.findFirst(query)['id']
    return KeycloakCRUD.get_child(kc, [client_id, child_resource])

class Clients(KeycloakCRUD):

    def secrets(self, client_query):
        obj = super().findFirst(client_query)
        child = KeycloakCRUD.get_child(self, [obj['id'], 'client-secret'])
        return child

    def get_roles(self, client_query):
        roles = self.roles(client_query).findAll().resp().json()
        return list(map(lambda role: Role(self, role), roles))

    def roles(self, client_query):
        client_id = super().findFirst(client_query)['id']
        child = KeycloakCRUD.get_child(self, [client_id, 'roles'])
        client_role_api = hack_rest_roles_remove_endpoint(self, child)

        return client_role_api
