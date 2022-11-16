import unittest

from .testbed import TestBed


class TestServerInfo(unittest.TestCase):
    def test_serverinfo_api(self):
        kc = self.testbed.getKeycloak()
        serverinfo_api = kc.build_serverinfo()

        serverinfo = serverinfo_api.get(None).verify().resp().json()

        self.assertIsInstance(serverinfo, dict)
        self.assertEqual("15.0.2", serverinfo["systemInfo"]["version"])
        self.assertEqual("community", serverinfo["profileInfo"]["name"])
        self.assertEqual("15.0.2", kc.server_info.version)
        self.assertEqual("community", kc.server_info.profile_name)

    @classmethod
    def setUpClass(self):
        self.testbed = TestBed()
        # self.testbed.createRealms()
        # self.testbed.createUsers()
        self.REALM = self.testbed.REALM

    @classmethod
    def tearDownClass(self):
        # self.testbed.goodBye()
        return 1
