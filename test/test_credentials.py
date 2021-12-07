import unittest, time
from rhsso import OpenID, KeycloakAdmin,RestURL
from .testbed import TestBed 
import json

USER = 'batman'
PASSWORD = '1234'

ADMIN_USER = "admin"
ADMIN_PSW  = "admin1234"
REALM = "test_heroes_test"
ENDPOINT = 'https://sso-cvaldezr-stage.apps.sandbox-m2.ll9k.p1.openshiftapps.com'



class Testing_User_API(unittest.TestCase):
    
    def test_adding_credentials_with_wrong_params(self):
        users = self.testbed.getKeycloak().build('users', REALM)
        user_info = {'key': 'username', 'value': 'batman'}
        user_credentials = {'temporary': False, 'passwordWrongParam':'12345'}
        try: 
            state = users.updateCredentials(user_info, user_credentials).isOk()
        except Exception as E:
            self.assertEqual("Missing parameter: value" in str(E), True)

    def test_adding_credentials_to_user(self):

        users = self.testbed.getKeycloak().build('users', REALM)
        user_info = {'key': 'username', 'value': 'batman'}
        user_credentials = {'temporary': False, 'value':'12345'}
        state = users.updateCredentials(user_info, user_credentials).isOk()
        self.assertTrue(state)

        oid_client = OpenID({
            "client_id": "dc",
            "username": "batman", 
            "password":"12345", 
            "grant_type":"password",
            "realm" : REALM 
            }, ENDPOINT)

        token = oid_client.getToken()
        self.assertNotEqual(token, None)

    @classmethod
    def setUpClass(self):
        self.testbed = TestBed(REALM, ADMIN_USER, ADMIN_PSW, ENDPOINT)
        self.testbed.createUsers()
        self.testbed.createClients()
        
    @classmethod
    def tearDownClass(self):
        self.testbed.goodBye()

if __name__ == '__main__':
    unittest.main()
