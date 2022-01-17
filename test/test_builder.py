import unittest, time
from kcapi.rest.builder import KCResourceBuilder
from kcapi.rest.idp import IdentityProvider 
from .testbed import TestBed
import json

def load_sample(fname):
    f = open(fname)
    file1 = json.loads(f.read())
    f.close()
    return file1

class Testing_User_API(unittest.TestCase):

    def testing_generic_build(self):

        endpoint = self.testbed.ENDPOINT
        realm = self.testbed.REALM
        token = self.testbed.token

        adm = KCResourceBuilder(endpoint).build(token) 
        roles = KCResourceBuilder(endpoint).withName('roles').forRealm(realm).build(token)

        self.assertIsNotNone(adm)
        self.assertIsNotNone(roles)
        
        self.assertTrue( roles.create({"name": "level-1"}).isOk() )


    def testing_concrete_classes_build(self):
        endpoint = self.testbed.ENDPOINT
        realm = self.testbed.REALM
        token = self.testbed.token

        users = KCResourceBuilder(endpoint).withName('users').forRealm(realm).build(token)
        self.assertTrue(hasattr(users, 'joinGroup'), 'joinGroup method not found in the Users class.')
        self.assertTrue(hasattr(users, 'groups'), 'groups method not found in the Users class.')




    @classmethod
    def setUpClass(self):
        self.testbed = TestBed()
        self.testbed.createRealms()
        self.REALM = self.testbed.REALM

    @classmethod
    def tearDownClass(self):
        #self.testbed.goodBye()
        return True

if __name__ == '__main__':
    unittest.main()
