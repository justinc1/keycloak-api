import requests, json
from .resp import ResponseHandler
from .url import RestURL

class KeycloakCRUD:
    def __req(self): 
        return requests 

    ''' 
        The guys at Keycloak don't use standard intuitive Rest path for all the activities,
        for example to create a car you can do:
            Post /car, 

        But to delete it you have to do:
            Delete /dealer/1, 

        Thats why we need this targets dictionary, to be able to modify the target when subclassing.  
    '''
    def __populate_targets(self, _url):
        url = RestURL(_url)

        targets = {
                    "create": url.copy(),
                    "update": url.copy(),
                    "delete": url.copy(),
                    "read":   url.copy(),
        }
        return targets
        
    def __init__(self, url = None, token = None, KeycloakAPI = {}): 
        self.token = token
        self.__targets = {}

        if url:
            self.resp = ResponseHandler(url)
            self.__targets = self.__populate_targets(url) 
        else:
            self.__targets = KeycloakAPI.make_copy_of_targets()

        if len(self.__targets) < 1:
            raise Exception('A list of URL targets are required.')

    
    def getMethod(self, name): 
        return self.__targets[name]

    def make_copy_of_targets(self):
        urls = {}
        for key in self.__targets: 
            urls[key] = self.__targets[key].copy()
        return urls 


    def getHeaders(self):
        return {
                'Content-type': 'application/json', 
                'Authorization': 'Bearer '+ self.token
        }

    def extend(self, resources): 
        kc = KeycloakCRUD(None, self.token, KeycloakAPI = self) 
        kc.addResources(resources)
        return kc

    def getURLs(self):
        return self.__targets 

    def changeTarget(self, resourceName): 
        for method in self.__targets: 
            self.__targets[method].replaceCurrentResourceTarget(resourceName)

    def removeResources(self, resources):
        for url in self.__targets: 
            url.removeResources(resources)
        return self

    def addResourcesFor(self, name, resources):
        self.__targets[name].addResources(resources)

    def addResources(self, resources): 
        for method in self.__targets: 
            self.__targets[method].addResources(resources)
        return self
        
    def __target(self, _id = None, url = None):
        if _id:
            return url.copy().addResource(_id)
        else:
            return url
    
    def create(self, obj):
        url = self.__targets['create']
        ret = requests.post(url, data=json.dumps(obj), headers=self.getHeaders() )
        return ResponseHandler(url, method='Post').handleResponse(ret)

    def update(self, _id=None, obj=None):
        url = self.__targets['update']
        target = str(self.__target(_id, url))

        ret = requests.put(target, data=json.dumps(obj), headers=self.getHeaders() )
        return ResponseHandler(target, method='Put').handleResponse(ret)

    def remove(self, _id):
        url = self.__target(_id, self.__targets['delete'])
        ret = requests.delete(url, headers=self.getHeaders() )
        return ResponseHandler(url, method='Delete').handleResponse(ret)
        
    def get(self, _id):
        url = self.__targets['read']
        ret = requests.get(str(self.__target(_id, url)), headers=self.getHeaders())
        return ResponseHandler(url, method='Get').handleResponse(ret)

    def findAll(self):
        url = self.__targets['read']
        ret = requests.get(url, headers=self.getHeaders())
        return ResponseHandler(url, method='Get').handleResponse(ret)


    def findFirst(self, params): 
        return self.findFirstByKV(params['key'], params['value'])

    def findFirstByKV(self, key, value):
        rows = self.findAll().verify().resp().json()

        if not rows:
            return False
        
        for row in rows: 
            if row[key].lower() == value.lower():
                return row

        return False

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

    def removeFirstByKV(self, key, value): 
        row = self.findFirstByKV(key,value)

        if row:
            return self.remove(row['id']).isOk()
        else:
            return False

    def existByKV(self, key, value): 
        ret = self.findFirstByKV(key, value)
        return ret != False

    def exist(self, _id):
        try:
            return self.get(_id).isOk()
        except Exception as E: 
            if "404" in str(E):
                return False
            else: 
                raise E

