import unittest, time
from rhsso import OpenID, KeycloakAdmin, Keycloak

rhsso_host = 'sso-cvaldezr-stage.apps.sandbox-m2.ll9k.p1.openshiftapps.com'
keycloak_root_endpoint = "https://sso-cvaldezr-stage.apps.sandbox-m2.ll9k.p1.openshiftapps.com"
resource = "my-realm-1"
USER = "admin"
PSW  = "admin1234"

class Testing_Relational_API(unittest.TestCase):

    def testing_adding_user_to_group(self):
        users = self.kc.build('users', self.test_realm)
        self.assertTrue(hasattr(users, "joinGroup"))

        usr = {"key": "username", "value": "batman"}
        gpr = {"key": "name", "value": "DC"}

        join_state = users.joinGroup(usr, gpr).isOk()
        self.assertTrue(join_state)

    def testing_that_group_has_changed(self):
        users = self.kc.build('users', self.test_realm)
        self.assertTrue(hasattr(users, "groups"))
        groups = users.groups({"key": "username", "value":"batman"})
        self.assertEqual(groups[0]['name'], 'DC')

    def testing_user_leaving_group(self):
        users = self.kc.build('users', self.test_realm)
        self.assertTrue(hasattr(users, "joinGroup"))

        usr = {"key": "username", "value": "batman"}
        gpr = {"key": "name", "value": "DC"}

        leave_status = users.leaveGroup(usr, gpr).isOk()
        self.assertTrue(leave_status)
        groups = users.groups(usr)
        self.assertEqual(len(groups), 0)
        

    @classmethod
    def setUpClass(self):
        self.test_realm = "realm_for_testing"
        self.token = OpenID.createAdminClient(USER, PSW).getToken(keycloak_root_endpoint)
        self.kc = Keycloak(self.token, keycloak_root_endpoint)
        self.master_realm = self.kc.admin()
        
        self.master_realm.create({"enabled": "true", "id": self.test_realm, "realm": self.test_realm})
        e = self.master_realm.exist(resource)

        test_users = [
                {"enabled":'true',"attributes":{},"username":"batman","firstName":"Bruce", "lastName":"Wayne", "emailVerified":""}, 
                {"enabled":'true',"attributes":{},"username":"superman","firstName":"Clark", "lastName":"Kent", "emailVerified":""}, 
                {"enabled":'true',"attributes":{},"username":"aquaman","firstName":"AAA%", "lastName":"Corrupt", "emailVerified":""}
        ]

        users = self.kc.build('users', self.test_realm)

        for usr in test_users: 
            users.create(usr).isOk()


        time.sleep(1)
        if e:
            self.master_realm.remove(resource)

        group = self.kc.build('groups', self.test_realm)
        g_creation_state = group.create({"name": "DC"}).isOk()


    @classmethod
    def tearDownClass(self):
        remove_state = self.master_realm.remove(self.test_realm)

        

if __name__ == '__main__':
    unittest.main()
