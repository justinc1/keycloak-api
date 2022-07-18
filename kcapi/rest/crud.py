import requests, json
from .resp import ResponseHandler

class KeycloakCRUD(object):
    _global_default_session = None

    @staticmethod
    def get_child(that, resource_id, resource_name):
        kc = KeycloakCRUD()
        kc.token = that.token
        kc.targets = that.targets.copy()

        kc.targets.addResources([resource_id, resource_name])

        return kc

    @classmethod
    def _get_default_session(cls):
        if KeycloakCRUD._global_default_session:
            return KeycloakCRUD._global_default_session
        # https://stackoverflow.com/a/66672380
        # Request will issue only one request over a single connection, at a time.
        # Connection is reused for a next request only when previous reply
        # is received AND consumed.
        KeycloakCRUD._global_default_session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=1000,
            pool_maxsize=100,
        )
        KeycloakCRUD._global_default_session.mount('https://', adapter)
        return KeycloakCRUD._global_default_session

    def __init__(self, session=None):
        self.targets = None
        self.token = None
        self.session = session or KeycloakCRUD._get_default_session()

    def headers(self):

        if self.token.expired():
            self.token = self.token.refresh()

        return {
                'Content-type': 'application/json', 
                'Authorization': 'Bearer '+ self.token.get_token()
        }

    def setIdentifier(self, _id = None, url = None):
        if _id:
            return url.addResource(_id)
        else:
            return url
    
    def create(self, payload):
        url = self.targets.url('create')

        ret = self.session.post(url, data=json.dumps(payload), headers=self.headers())
        return ResponseHandler(url, method='Post', payload=payload).handleResponse(ret)

    def update(self, obj_id=None, payload=None):
        url = self.targets.url('update')
        target = str(self.setIdentifier(obj_id, url))

        ret = self.session.put(target, data=json.dumps(payload), headers=self.headers())
        return ResponseHandler(target, method='Put', payload=payload).handleResponse(ret)

    def remove(self, _id):
        delete = self.targets.url('delete')
        url = self.setIdentifier(_id, delete)
        ret = self.session.delete(url, headers=self.headers())
        return ResponseHandler(url, method='Delete').handleResponse(ret)
        
    def get(self, _id):
        url = self.targets.url('read')
        ret = self.session.get(str(self.setIdentifier(_id, url)), headers=self.headers())
        return ResponseHandler(url, method='Get').handleResponse(ret)

    def findAll(self):
        url = self.targets.url('read')
        ret = self.session.get(url, headers=self.headers())
        return ResponseHandler(url, method='Get').handleResponse(ret)

    # Search for user by email, firstName, lastName, etc.
    # This can be used with /users/ API endpoint,
    # but not with /groups/ (see API definition).
    def search(self, params):
        url = self.targets.url('read')
        ret = self.session.get(url, params=params, headers=self.headers())
        responses = ResponseHandler(url, method='Get').handleResponse(ret)
        return responses.verify().resp().json()

    # Count object. Works only for /users/.
    def count(self):
        url = self.targets.url('read')
        url.pushResource('count')
        ret = self.session.get(url, headers=self.headers())
        responses = ResponseHandler(url, method='Get').handleResponse(ret)
        return responses.verify().resp().json()

    def findFirst(self, params):
        return self.findFirstByKV(params['key'], params['value'])

    def findFirstByKV(self, key, value):
        rows = self.findAll().verify().resp().json()

        for row in rows: 
            if row[key].lower() == value.lower():
                return row

        return []

    def all(self):
        return self.findAll().verify().resp().json()

    def updateUsingKV(self, key, value, obj): 
        res_data = self.findFirstByKV(key,value)

        if res_data: 
            data_id = res_data['id']
            res_data.update(obj)
            return self.update(data_id, res_data).isOk() 
        else:
            return False

    def removeFirstByKV(self, key, value, custom_key="id"):
        row = self.findFirstByKV(key,value)

        if row:
            return self.remove(row[custom_key]).isOk()
        else:
            return False

    def existByKV(self, key, value): 
        ret = self.findFirstByKV(key, value)
        return ret != False

    def exist(self, _id):
        return self.get(_id).ok()


