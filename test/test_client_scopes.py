import unittest, time
from copy import copy

from .testbed import TestBed, KcBaseTestCase


class TestClientScopesCRUD(KcBaseTestCase):
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


if __name__ == '__main__':
    unittest.main()
