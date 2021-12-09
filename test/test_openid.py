import unittest, time
from rhsso import OpenID, RestURL

wrong_URL = 'https://sso-cvaldezr-dev.apps.sandbox.x8i5.p1.openshiftapps.com'
good_URL = 'https://sso-cvaldezr-stage.apps.sandbox-m2.ll9k.p1.openshiftapps.com'
USER = 'admin'
PASSWORD = 'admin1234'


class Testing_OpenID(unittest.TestCase):
    def test_oidc_ctor(self): 
        try:
            OpenID({"client_id":"admin-cli"}, wrong_URL)
        except Exception as E:
            self.assertEqual("password" in str(E), True)

        try:
            OpenID({"client_id":"admin-cli", "realm": "my_realm", "password": "xxx"}, wrong_URL)
        except Exception as E:
            self.assertEqual("username" in str(E), True)

        self.assertRaises(Exception, lambda: OpenID({"client_id":"admin-cli"})) 

    def test_oidc_login_on_wrong_url(self):
        oid_client = OpenID({
            "client_id": "admin-cli",
            "username": "6OPtWY33", 
            "password":"I6gglTeDLlmmpLYoAAUMcFQqNOMjw5dA", 
            "grant_type":"password",
            "realm" : "master"
            }, wrong_URL)
        
        self.assertRaises(Exception, lambda: oid_client.getToken()) 

    def test_oidc_login_on_wrong_password(self):
        oid_client = OpenID({
            "client_id": "admin-cli",
            "username": "6OPtWY33", 
            "password":"I6gglTeDLlmmpLYoAAUMcFQqNOMjw5dA", 
            "grant_type":"password",
            "realm" : "master"
            }, good_URL)

        try:
            oid_client.getToken()
        except Exception as E:
            self.assertEqual("Unauthorized" in str(E), True)

    def test_creating_oidc_client_using_factory(self):
        oidc = OpenID.createAdminClient(USER, PASSWORD)
        self.assertIsNotNone( oidc.getToken(good_URL) )

    def test_oidc_login(self):
        oid_client = OpenID({
            "client_id": "admin-cli",
            "username": "admin", 
            "password":"admin1234", 
            "grant_type":"password",
            "realm" : "master"
            }, good_URL)

        token = oid_client.getToken()
        self.assertIsNotNone(token)
        self.assertEqual(len(token), 1011)
        

if __name__ == '__main__':
    unittest.main()
