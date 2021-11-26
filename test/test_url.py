import unittest, time
from rhsso import RestURL 

class Testing_URL_API(unittest.TestCase):

    def testing_only_setting_hostname(self): 
        try:
            my_url = RestURL('my-host')
        except Exception as E:
            self.assertEqual("schema" in str(E), True)


        my_url = RestURL('https://my-host')
        self.assertEqual('https://my-host', str(my_url))
        _url = my_url.copy()
        self.assertEqual('https://my-host', str(_url))

    def testing_obj_construction(self):
        self.assertRaises(Exception, lambda: RestURL()) 
        nurl = RestURL(self.endpoint)
        self.assertEqual(str(nurl), self.endpoint)

    def testing_adding_resources(self):
        url = self.url.copy()
        url.addResource("auth", "admin")
        test1 = self.endpoint + "/auth/admin"
        test2 = self.endpoint + "/auth/admin/realms/AAA/client-templates/my_client/scope-mappings/clients/123"
        test3 = self.endpoint + "/auth/admin/realms/AAA/client-templates/my_client_1/scope-mappings/clients/542"

        self.assertEqual(str(url), test1)
        url.addResource("realms", "AAA")

        t1 = url.copy()
        t2 = url.copy()

        t1.addResource("client-templates", "my_client")
        t2.addResource("client-templates", "my_client_1")

        t1.addResource("scope-mappings", "clients")
        t2.addResource("scope-mappings", "clients")

        t1.addResource("clients", "123")
        t2.addResource("clients", "542")

        self.assertEqual(str(t1), test2)
        self.assertEqual(str(t2), test3)

    def testing_single_entry_resources(self):
        url = self.url.copy()

        url.addResources([])
        self.assertEqual(str(url), self.endpoint)

        url.addResources(["auth"])
        self.assertEqual(str(url), self.endpoint + "/auth")
    
    def testing_multiple_entries(self):
        url = self.url.copy()
        raw_str = "/auth/admin/realms/aaa/client-templates/my_client/scope-mappings/clients/123"
        test = raw_str.split("/")
        test =  list( filter(lambda n: n != "", test) )
        url.addResources(test)
        self.assertEqual(str(url), self.endpoint + raw_str)


    def testing_resource_replacement(self):
        url = self.url.copy()
        raw_str = "/auth/admin/realms/aaa/roles"
        test = raw_str.split("/")
        test =  list( filter(lambda n: n != "", test) )
        url.addResources(test)
        self.assertEqual(str(url), self.endpoint + raw_str)

        url.replaceResource('roles', 'roles-by-id')
        self.assertEqual(str(url), self.endpoint + "/auth/admin/realms/aaa/roles-by-id")


    def testing_getting_actual_resource(self):
        self.assertEqual(self.url.getCurrentResource(), "resource1")

    def testing_getting_target(self):
        self.assertEqual(self.url.target(), "https://my-sso.com")




    def testing_removing_resources(self):
        url = "https://my-sso.com"
        myURL = self.url.copy()
        myURL.removeResources(["resource1", "res2"])
        self.assertEqual(str(myURL), url)


    @classmethod
    def setUpClass(self):
        self.endpoint = "https://my-sso.com/resource1"
        self.url = RestURL(self.endpoint)

if __name__ == '__main__':
    unittest.main()
