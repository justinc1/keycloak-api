import unittest, time
from kcapi.rest.crud import KeycloakCRUD
from kcapi.rest.targets import Targets
from kcapi.rest.url import RestURL
from .testbed import TestBed
import json

def load_sample(fname):
    f = open(fname)
    file1 = json.loads(f.read())
    f.close()
    return file1

def exist(that, res, name):
    ret  = res.findFirstByKV('username', name)
    that.assertEqual(name, ret['firstName'], 'We expect a role ['+name+'] to be created')
    return ret['id']



def test_complete_CRUD(that, users):
        ## POST
        state = users.create(that.USER_DATA)
        that.assertTrue(state, 'fail while posting')
     
        ret  = users.findFirstByKV('username', 'pepe')
        that.assertEqual('pepe', ret['firstName'], 'We expect a user with pepe as username to be created')
        
        ## UPDATE
        state = users.update(ret['id'], {'firstName': 'pedro'})
        that.assertTrue(state, 'fail while updating')
        
        ret  = users.findFirstByKV('firstName', 'pedro')
        that.assertTrue(ret != False, 'Something wrong updating the resource.')
        that.assertEqual('pedro', ret['firstName'], 'We expect a user with pepe as username to be created')
        
        ## GET
        usr = users.get(ret['id']).resp().json()
        that.assertEqual(ret['id'], usr['id'])
        
        _all = users.all()
        that.assertEqual(len(_all), 4, 'All users amount to one')


        ## DELETE
        remove_state = users.remove(ret['id']).isOk()
        that.assertTrue(remove_state)
        removed = users.findFirstByKV('firstName', 'pedro')

        that.assertFalse(removed)


class SlowFile:
    def __init__(self, content, delays=[]):
        self.content = bytes(content, 'utf-8')
        self.delays = delays
        self.ii = -1

    def __iter__(self):
        # self.ii = -1
        return self

    def __next__(self):
        self.ii += 1
        if self.ii >= len(self.content):
            raise StopIteration
        return self.content[self.ii: self.ii+1]


class Testing_User_API(unittest.TestCase):

    def testing_crud_API(self):
        token = self.testbed.token

        users = KeycloakCRUD()
        users.targets = Targets.makeWithURL(str(self.USER_ENDPOINT))
        users.token = token

        test_complete_CRUD(self, users)

    def test_slow_CRUD(self):
        """
        We want to test  test if long lasting requests can complete.
        We monkey patch requests.put to achieve long upload time.
        The access_token expires in 60 sec.
        Assumption is that access_token is verified at beginning of request only.
        """
        token = self.testbed.token
        users = KeycloakCRUD()
        users.targets = Targets.makeWithURL(str(self.USER_ENDPOINT))
        users.token = token

        ## IS PRESENT
        user_present = users.findFirstByKV('firstName', 'pepe')
        self.assertFalse(user_present)

        ## POST
        # state = users.create(self.USER_DATA)
        # inline code for users.create()
        def users_create(obj, payload):
            import requests
            from kcapi.rest.resp import ResponseHandler
            url = obj.targets.url('create')
            data_file = SlowFile(json.dumps(payload), [])
            ret = requests.post(url, data=data_file, headers=obj.headers())
            return ResponseHandler(url, method='Post', payload=payload).handleResponse(ret)

        state = users_create(users, self.USER_DATA)
        self.assertTrue(state, 'fail while posting')

        ret = users.findFirstByKV('username', 'pepe')
        self.assertEqual('pepe', ret['firstName'], 'We expect a user with pepe as username to be created')

        ## DELETE
        remove_state = users.remove(ret['id']).isOk()
        self.assertTrue(remove_state)
        ## IS PRESENT
        user_present = users.findFirstByKV('firstName', 'pepe')
        self.assertFalse(user_present)

    @classmethod
    def setUpClass(self):
       
        self.testbed = TestBed()
        self.testbed.createRealms()
        self.testbed.createUsers()
        self.REALM = self.testbed.REALM
       
        self.USER_ENDPOINT = RestURL(self.testbed.ENDPOINT)
        self.USER_ENDPOINT.addResources(['auth', 'admin', 'realms', self.REALM, 'users']) 

        self.USER_DATA = {"enabled":True,"attributes":{},"username":"pepe","emailVerified":"", "firstName": 'pepe'}
       
    @classmethod
    def tearDownClass(self):
        self.testbed.goodBye()
        return True

if __name__ == '__main__':
    unittest.main()
