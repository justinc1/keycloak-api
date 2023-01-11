import unittest, time
from copy import copy

from kcapi.rest.crud import KeycloakCRUD

from kcapi.rest.client_scopes import ClientScopeScopeMappingsCRUD
from .testbed import TestBed, KcBaseTestCase


class BaseClientScopesTestCase(KcBaseTestCase):
    vcr_enabled = False
    default_client_scope_name = sorted([
        'address',
        'email',
        'microprofile-jwt',
        'offline_access',
        'phone',
        'profile',
        'role_list',
        'roles',
        'web-origins',
    ])

    client_scope_name = "ci0-client-scope-0"
    client_scope_doc = {
        "name": client_scope_name,
        "description": client_scope_name + "-desc",
        "protocol": "openid-connect",
        "attributes": {
            "display.on.consent.screen": "true",
            "include.in.token.scope": "true"
        },
    }

    def setUp(self, *, create_all=True):
        super().setUp(create_all=False)

        if self.testbed.master_realm.exist(self.testbed.realm):
            state = self.testbed.master_realm.remove(self.testbed.realm).ok()

        self.testbed.createRealms()
        # self.testbed.createUsers()
        # self.testbed.createClients()

    def tearDown(self):
        # VCRTestCase.tearDown is not called!
        pass


class TestClientScopesCRUD(BaseClientScopesTestCase):
    def test_list(self):
        client_scopes_api = self.testbed.kc.build("client-scopes", self.testbed.realm)
        client_scopes = client_scopes_api.all()
        self.assertEqual(9, len(client_scopes), "by default there are 9 client scopes")
        self.assertEqual(
            self.default_client_scope_name,
            [client_scope["name"] for client_scope in client_scopes],
        )

    def test_list2(self):
        client_scopes_api = self.testbed.kc.build("client-scopes", self.testbed.realm)
        client_scopes = client_scopes_api.all()
        self.assertEqual(9, len(client_scopes), "by default there are 9 client scopes")
        self.assertEqual(
            self.default_client_scope_name,
            [client_scope["name"] for client_scope in client_scopes],
        )

    def test_create(self):
        client_scopes_api = self.testbed.kc.build("client-scopes", self.testbed.realm)
        client_scopes = client_scopes_api.all()
        old_count = len(client_scopes)

        client_scopes_api.create(self.client_scope_doc)
        #
        client_scopes = client_scopes_api.all()
        new_count = len(client_scopes)
        self.assertEqual(old_count + 1, new_count)
        client_scope = client_scopes_api.findFirstByKV("name", self.client_scope_name)
        client_scope_min = copy(client_scope)
        client_scope_min.pop("id")
        self.assertEqual(
            self.client_scope_doc,
            client_scope_min,
        )

    def test_update(self):
        client_scopes_api = self.testbed.kc.build("client-scopes", self.testbed.realm)

        client_scopes_api.create(self.client_scope_doc)
        client_scope_a = client_scopes_api.findFirstByKV("name", self.client_scope_name)
        client_scope_id = client_scope_a["id"]
        client_scope_min = copy(client_scope_a)
        client_scope_min.pop("id")
        self.assertEqual(
            self.client_scope_doc,
            client_scope_min,
        )

        # update
        client_scope_doc2 = copy(self.client_scope_doc)
        client_scope_doc2.update({
            "description": "ci0-client-scope-0-desc-NEW",
            "attributes": {
                "display.on.consent.screen": "false",
                "include.in.token.scope": "true",
            },
        })
        client_scopes_api.update(client_scope_id, client_scope_doc2)
        #
        client_scope_b = client_scopes_api.findFirstByKV("name", self.client_scope_name)
        self.assertEqual(client_scope_id, client_scope_b["id"])
        client_scope_min = copy(client_scope_b)
        client_scope_min.pop("id")
        self.assertEqual(
            client_scope_doc2,
            client_scope_min,
        )

    def test_scope_mappings_api(self):
        client_scopes_api = self.testbed.kc.build("client-scopes", self.testbed.realm)
        client_scopes_api.create(self.client_scope_doc)
        client_scope = client_scopes_api.findFirstByKV("name", self.client_scope_name)
        client_scope_id = client_scope["id"]

        this_client_scope_scope_mappings_api = client_scopes_api.scope_mappings_api(client_scope_id=client_scope_id)
        self.assertIsInstance(this_client_scope_scope_mappings_api, ClientScopeScopeMappingsCRUD)


class TestClientScopeScopeMappingsCRUD(BaseClientScopesTestCase):
    def test_list(self):
        realm_roles_api = self.testbed.kc.build("roles", self.testbed.realm)
        client_scopes_api = self.testbed.kc.build("client-scopes", self.testbed.realm)
        clients_api = self.testbed.kc.build("clients", self.testbed.realm)

        client_scopes_api.create(self.client_scope_doc)
        client_scope = client_scopes_api.findFirstByKV("name", self.client_scope_name)
        client_scope_id = client_scope["id"]

        # -----------------------------------------
        # List client-scope with no mappings
        this_client_scope_scope_mappings_api = client_scopes_api.scope_mappings_api(client_scope_id=client_scope_id)
        self.assertEqual({}, this_client_scope_scope_mappings_api.all())

        # -----------------------------------------
        # List client-scope with one realm role
        # create one mapping to realm role
        realm_role_name = "offline_access"
        realm_role = realm_roles_api.findFirstByKV("name", realm_role_name)
        this_client_scope_scope_mappings_realm_api = KeycloakCRUD.get_child(this_client_scope_scope_mappings_api, None, "realm")
        this_client_scope_scope_mappings_realm_api.create([realm_role])
        realm_role_min = copy(realm_role)
        realm_role_min.pop("attributes")
        expected_scope_mappings = {
            # "clientMappings": ,
            "realmMappings": [
                realm_role_min,
            ]
        }

        # test output
        scope_mappings = this_client_scope_scope_mappings_api.all()
        self.assertEqual(expected_scope_mappings, scope_mappings)

        # -----------------------------------------
        # List client-scope with one realm role and one client role
        # create one mapping to client role
        client_clientId = "account"
        client_role_name = "view-profile"
        client = clients_api.findFirstByKV("clientId", client_clientId)
        account_client_roles_api = clients_api.roles(dict(key="clientId", value=client_clientId))
        client_role = account_client_roles_api.findFirstByKV("name", client_role_name)
        this_client_scope_scope_mappings_client_account_api = KeycloakCRUD.get_child(this_client_scope_scope_mappings_api, None, f"clients/{client['id']}")
        this_client_scope_scope_mappings_client_account_api.create([client_role])
        client_role_min = copy(client_role)
        client_role_min.pop("attributes")
        expected_scope_mappings = {
            "clientMappings": {
                "account": {
                    "client": "account",
                    "id": client["id"],
                    "mappings": [
                        client_role_min,
                    ],
                }
            },
            "realmMappings": [
                realm_role_min,
            ]
        }

        # test output
        scope_mappings = this_client_scope_scope_mappings_api.all()
        self.assertEqual(expected_scope_mappings, scope_mappings)


if __name__ == '__main__':
    unittest.main()
