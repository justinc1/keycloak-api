import unittest, time
from rhsso import OpenID, Keycloak
from .testbed import TestBed 

ADMIN_USER = "admin"
ADMIN_PSW  = "admin1234"
REALM = "test_heroes_test"
ENDPOINT = 'https://sso-cvaldezr-stage.apps.sandbox-m2.ll9k.p1.openshiftapps.com'

class Testing_Relational_API(unittest.TestCase):

    def testing_adding_user_to_group(self):
        users = self.kc.build('users', self.realm)
        self.assertTrue(hasattr(users, "joinGroup"))

        usr = {"key": "username", "value": "batman"}
        gpr = {"key": "name", "value": "DC"}

        join_state = users.joinGroup(usr, gpr).isOk()
        self.assertTrue(join_state)

    def testing_that_group_has_changed(self):
        users = self.kc.build('users', self.realm)
        self.assertTrue(hasattr(users, "groups"))
        groups = users.groups({"key":"username", "value":"batman"})
        self.assertEqual(groups[0]['name'], 'DC')

    def testing_user_leaving_group(self):
        users = self.kc.build('users', self.realm)
        self.assertTrue(hasattr(users, "joinGroup"))

        usr = {"key": "username", "value": "batman"}
        gpr = {"key": "name", "value": "DC"}

        leave_status = users.leaveGroup(usr, gpr).isOk()
        self.assertTrue(leave_status)
        groups = users.groups(usr)
        self.assertEqual(len(groups), 0)

    def testing_adding_roles_to_group(self): 
        groups = self.kc.build('groups', self.realm)
        self.assertTrue(hasattr(groups, "realmRoles"))

        #TestBed class will create one group called "DC" 
        #And three roles called [level-1, level-2, level-3]

        group = {"key":"name", "value":'DC'}
        roles_mapping = groups.realmRoles(group)
        state = roles_mapping.add(["level-1", "level-2"])
        self.assertTrue(state)

        realmRoles = roles_mapping.all()
        self.assertEqual(len(realmRoles), 2)

        roles_mapping.remove(["level-1", "level-2"])
        self.assertEqual(len(roles_mapping.all()), 0)

    @classmethod
    def setUpClass(self):
        self.testbed = TestBed()
        self.testbed.createRealms()
        self.testbed.createUsers()
        self.testbed.createClients()
        self.testbed.createGroups()
        self.kc = self.testbed.getKeycloak()
        self.realm = self.testbed.REALM 
        
    @classmethod
    def tearDownClass(self):
        #self.testbed.goodBye()
        return True

if __name__ == '__main__':
    unittest.main()
