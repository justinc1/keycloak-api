import unittest, time
from kcapi import OpenID, RestURL
from kcapi.rest.idp import IdentityProvider 
from .testbed import TestBed
import json

def load_sample(fname):
    f = open(fname)
    file1 = json.loads(f.read())
    f.close()
    return file1

class Testing_User_API(unittest.TestCase):

    def test_adding_credentials_to_user(self):

        idp = self.testbed.getKeycloak().build('identity-provider', self.REALM)

        self.assertIsNotNone(idp)
    
        self.assertTrue(hasattr(IdentityProvider, 'supportedResources'))
        self.assertTrue(hasattr(IdentityProvider, 'build'))
        
        self.assertTrue(IdentityProvider.supportedResources('idp'))
        self.assertTrue(IdentityProvider.supportedResources('identity-provider'))
        self.assertFalse(IdentityProvider.supportedResources('arbitrary'))

    def test_creating_and_object(self):
        endpoint = self.testbed.ENDPOINT
        realm = self.testbed.REALM
        token = self.testbed.token

        idp = IdentityProvider.build(url=endpoint, realm=realm, token=token)

        saml = load_sample('./test/payloads/idp_saml.json')
        oid = load_sample('./test/payloads/idp_oid.json')
        state = idp.create(saml).isOk()
        self.assertTrue(state)
        
        state = idp.create(oid).isOk()
        self.assertTrue(state)

    @classmethod
    def setUpClass(self):
        self.testbed = TestBed()
        self.testbed.createRealms()
        self.testbed.createUsers()
        self.testbed.createClients()
        self.REALM = self.testbed.REALM

    @classmethod
    def tearDownClass(self):
        #self.testbed.goodBye()
        return True

if __name__ == '__main__':
    unittest.main()
