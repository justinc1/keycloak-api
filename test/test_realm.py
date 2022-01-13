import unittest, time
from kcapi import OpenID, RestURL
from .testbed import TestBed
import json

class Testing_Realm_API(unittest.TestCase):

    '''
    def test_adding_credentials_with_wrong_params(self):
        users = self.testbed.getKeycloak().build('users', self.REALM)
        user_info = {'key': 'username', 'value': 'batman'}
        user_credentials = {'temporary': False, 'passwordWrongParam':'12345'}
        try: 
            state = users.updateCredentials(user_info, user_credentials).isOk()
        except Exception as E:
            self.assertEqual("Missing parameter: value" in str(E), True)

    '''
    
    def testing_realm_api_methods(self):
        realms = self.testbed.getKeycloak().build('realms', self.REALM)
        self.assertTrue(hasattr(realms, 'caches'))


    def testing_realm_cache_reset(self):
        realms = self.testbed.getKeycloak().build('realms', self.REALM)

        caches = realms.caches(self.REALM)

        self.assertEqual(caches.clearRealmCache().resp().status_code, 204)

    def testing_user_cache_reset(self):
        realms = self.testbed.getKeycloak().build('realms', self.REALM)

        caches = realms.caches(self.REALM)

        self.assertEqual(caches.clearUserCache().resp().status_code, 204)


    def testing_key_cache_reset(self):
        realms = self.testbed.getKeycloak().build('realms', self.REALM)

        caches = realms.caches(self.REALM)

        self.assertEqual(caches.clearKeyCache().resp().status_code, 204)


    @classmethod
    def setUpClass(self):
        self.testbed = TestBed()
        self.testbed.createRealms()
        self.testbed.createUsers()
        self.testbed.createClients()
        self.REALM = self.testbed.REALM

    @classmethod
    def tearDownClass(self):
        self.testbed.goodBye()

if __name__ == '__main__':
    unittest.main()
