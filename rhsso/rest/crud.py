import requests, json
from .resp import ResponseHandler
from .url import RestURL

class KeycloakCRUD:
    def __req(self): 
        return requests 

    def __init__(self, url, token): 
        self.resource_url = RestURL(url)
        self.token = token
        self.resp = ResponseHandler(url)

    def getHeaders(self):
        return {
                'Content-type': 'application/json', 
                'Authorization': 'Bearer '+ self.token
                }

    def extend(self, list_res): 
        newURL = self.resource_url.copy()
        newURL.addResources(list_res)

        return KeycloakCRUD(str(newURL), self.token) 

    def getURL(self):
        return self.resource_url

    def buildNew(self, resourceName): 
        newURL = self.resource_url.copy()
        newURL.replaceCurrentResourceTarget(resourceName)
        return KeycloakCRUD(str(newURL), self.token) 
        
    def __target(self, _id):
        url = self.resource_url.copy()
        url.addResource(_id)
        return url
    
    def create(self, obj):
        ret = requests.post(self.resource_url, data=json.dumps(obj), headers=self.getHeaders() )
        return self.resp.handleResponse(ret)

    def update(self, _id, obj):
        target = str(self.__target(_id))
        ret = requests.put(str(self.__target(_id)), data=json.dumps(obj), headers=self.getHeaders() )
        return self.resp.handleResponse(ret)

    def remove(self, _id):
        ret = requests.delete(str(self.__target(_id)), headers=self.getHeaders() )
        #return ResponseHandler(ret).no_content()
        return self.resp.handleResponse(ret)
        
    def findById(self, _id):
        ret = requests.get(str(self.__target(_id)), headers=self.getHeaders())
        #return ResponseHandler(ret).resp().json()
        return self.resp.handleResponse(ret)


    def findFirst(self, params): 
        return self.findFirstByKV(params['key'], params['value'])

    def findFirstByKV(self, key, value):
        try: 
            rows = self.findAll().verify().resp().json()
            for row in rows: 
                if row[key].lower() == value.lower():
                    return row

        except Exception as E: 
            if "404" in str(E): 
                return False 

        return False

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

    def findAll(self):
        ret = requests.get(self.resource_url, headers=self.getHeaders())
        return self.resp.handleResponse(ret)

    def exist(self, _id):
        try:
            return self.findById(_id).isOk()
        except Exception as E: 
            if "404" in str(E):
                return False
            else: 
                raise E

