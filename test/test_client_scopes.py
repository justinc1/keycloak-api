import unittest, time
from copy import copy

from kcapi.rest.crud import KeycloakCRUD

from kcapi.rest.client_scopes import ClientScopeScopeMappingsCRUD, ClientScopeProtocolMapperCRUD
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

    def setUp(self):
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

    def test_get_subobjects_api(self):
        client_scopes_api = self.testbed.kc.build("client-scopes", self.testbed.realm)
        client_scopes_api.create(self.client_scope_doc)
        client_scope = client_scopes_api.findFirstByKV("name", self.client_scope_name)
        client_scope_id = client_scope["id"]

        this_client_scope_scope_mappings_api = client_scopes_api.scope_mappings_api(client_scope_id=client_scope_id)
        self.assertIsInstance(this_client_scope_scope_mappings_api, ClientScopeScopeMappingsCRUD)
        this_client_scope_protocol_mapper_api = client_scopes_api.protocol_mapper_api(client_scope_id=client_scope_id)
        self.assertIsInstance(this_client_scope_protocol_mapper_api, ClientScopeProtocolMapperCRUD)


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


class TestClientScopeScopeMappingsRealmCRUD(BaseClientScopesTestCase):

    def setUp(self):
        super().setUp()
        self.client_scopes_api = self.testbed.kc.build("client-scopes", self.testbed.realm)
        client_scopes_api = self.client_scopes_api
        client_scopes_api.create(self.client_scope_doc)
        self.client_scope = self.client_scopes_api.findFirstByKV("name", self.client_scope_name)
        # client_scope_id = self.client_scope["id"]

    def test_list(self):
        realm_roles_api = self.testbed.kc.build("roles", self.testbed.realm)
        client_scopes_api = self.testbed.kc.build("client-scopes", self.testbed.realm)
        clients_api = self.testbed.kc.build("clients", self.testbed.realm)
        client_scope_id = self.client_scope["id"]
        this_client_scope_scope_mappings_realm_api = client_scopes_api.scope_mappings_realm_api(client_scope_id=client_scope_id)

        # -----------------------------------------
        # List client-scope with no mappings
        self.assertEqual([], this_client_scope_scope_mappings_realm_api.all())

    def test_create_remove(self):
        realm_roles_api = self.testbed.kc.build("roles", self.testbed.realm)
        client_scopes_api = self.testbed.kc.build("client-scopes", self.testbed.realm)
        clients_api = self.testbed.kc.build("clients", self.testbed.realm)
        client_scope_id = self.client_scope["id"]
        this_client_scope_scope_mappings_realm_api = client_scopes_api.scope_mappings_realm_api(client_scope_id=client_scope_id)
        realm_role0_name = "offline_access"
        realm_role0 = realm_roles_api.findFirstByKV("name", realm_role0_name)
        realm_role0_min = copy(realm_role0)
        realm_role0_min.pop("attributes")
        realm_role1_name = "uma_authorization"
        realm_role1 = realm_roles_api.findFirstByKV("name", realm_role1_name)
        realm_role1_min = copy(realm_role1)
        realm_role1_min.pop("attributes")

        # -----------------------------------------
        # Create 1st mapping
        this_client_scope_scope_mappings_realm_api.create([realm_role0]).isOk()
        self.assertEqual([realm_role0_min], this_client_scope_scope_mappings_realm_api.all())
        # Create 2nd mapping - it is added to 1st.
        this_client_scope_scope_mappings_realm_api.create([realm_role1]).isOk()
        self.assertEqual(
            sorted([realm_role0_min, realm_role1_min], key=lambda d: d['name']),
            sorted(this_client_scope_scope_mappings_realm_api.all(), key=lambda d: d['name']),
        )

        # -----------------------------------------
        # Remove 1st mapping, 2nd one is left
        this_client_scope_scope_mappings_realm_api.remove(None, [realm_role0]).isOk()
        self.assertEqual([realm_role1_min], this_client_scope_scope_mappings_realm_api.all())
        # Remove 2nd mapping.
        this_client_scope_scope_mappings_realm_api.remove(None, [realm_role1]).isOk()
        self.assertEqual([], this_client_scope_scope_mappings_realm_api.all())

# TODO TestClientScopeScopeMappingsClientCRUD


class TestClientScopeScopeMapperCRUD(BaseClientScopesTestCase):
    """
    If "protocolMappers" added to client_scope_doc, then:
    - if client_scope is created, protocolMappers are added to it.
    - if client_scope is updated, protocolMappers are ignored.
    """

    protocol_mapper_docs = [
        # In web UI, select "Create", mapper type == "user attribute"
        {
            "config": {
                "access.token.claim": "true",
                "claim.name": "birthdate",
                "id.token.claim": "true",
                "jsonType.label": "String",
                "user.attribute": "birthdate",
                "userinfo.token.claim": "true"
            },
            "consentRequired": False,
            "name": "birthdate",
            "protocol": "openid-connect",
            "protocolMapper": "oidc-usermodel-attribute-mapper"
        },
        # In web UI, select "Add builtin", zoneinfo
        {
            "name": "zoneinfo",
            "protocol": "openid-connect",
            "protocolMapper": "oidc-usermodel-attribute-mapper",
            "consentRequired": False,
            "config": {
                "userinfo.token.claim": "true",
                "user.attribute": "zoneinfo",
                "id.token.claim": "true",
                "access.token.claim": "true",
                "claim.name": "zoneinfo",
                "jsonType.label": "String",
            },
        },
    ]

    def setUp(self):
        super().setUp()
        self.client_scopes_api = self.testbed.kc.build("client-scopes", self.testbed.realm)
        client_scopes_api = self.client_scopes_api
        client_scopes_api.create(self.client_scope_doc)
        self.client_scope = self.client_scopes_api.findFirstByKV("name", self.client_scope_name)
        # client_scope_id = self.client_scope["id"]

    def test_list(self):
        client_scopes_api = self.client_scopes_api
        client_scope_id = self.client_scope["id"]
        this_client_scope_protocol_mapper_api = client_scopes_api.protocol_mapper_api(client_scope_id=client_scope_id)

        # -----------------------------------------
        # List client-scope with no mappings
        self.assertEqual([], this_client_scope_protocol_mapper_api.all())

    def test_create_remove(self):
        client_scopes_api = self.client_scopes_api
        client_scope_id = self.client_scope["id"]
        this_client_scope_protocol_mapper_api = client_scopes_api.protocol_mapper_api(client_scope_id=client_scope_id)

        # -----------------------------------------
        # Create 1st mapper
        this_client_scope_protocol_mapper_api.create(self.protocol_mapper_docs[0]).isOk()
        protocol_mappers_min = this_client_scope_protocol_mapper_api.all()
        for pm in protocol_mappers_min:
            pm.pop("id")
        self.assertEqual([self.protocol_mapper_docs[0]], protocol_mappers_min)
        # Create 2nd mapping
        this_client_scope_protocol_mapper_api.create(self.protocol_mapper_docs[1]).isOk()
        protocol_mappers_min = this_client_scope_protocol_mapper_api.all()
        for pm in protocol_mappers_min:
            pm.pop("id")
        self.assertEqual(
            sorted(self.protocol_mapper_docs, key=lambda d: d['name']),
            sorted(protocol_mappers_min, key=lambda d: d['name']),
        )

        # -----------------------------------------
        # Remove 1st mapper, 2nd one is left
        protocol_mappers = this_client_scope_protocol_mapper_api.all()
        protocol_mappers = sorted(protocol_mappers, key=lambda d: d['name'])
        self.assertEqual(["birthdate", "zoneinfo"], [pm["name"] for pm in protocol_mappers])
        # Remove 1st mapper
        this_client_scope_protocol_mapper_api.remove(protocol_mappers[0]["id"], None).isOk()
        self.assertEqual([protocol_mappers[1]], this_client_scope_protocol_mapper_api.all())
        # Remove 2nd mapper.
        this_client_scope_protocol_mapper_api.remove(protocol_mappers[1]["id"], None).isOk()
        self.assertEqual([], this_client_scope_protocol_mapper_api.all())


if __name__ == '__main__':
    unittest.main()
