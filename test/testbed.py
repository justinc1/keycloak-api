from rhsso import OpenID, KeycloakAdmin, Keycloak

def readFromJSON(filename):
    with open(filename) as json_file:
        return json.load(json_file)

class TestBed:
    def __init__(self, realm, username, password, endpoint): 
        token = OpenID.createAdminClient(username, password).getToken(endpoint)
        self.kc = Keycloak(token, endpoint)
        self.master_realm = self.kc.admin()
        
        self.master_realm.create({"enabled": "true", "id": realm, "realm": realm})


        self.realm = realm 


    def createClients(self):
        realm = self.realm
        client = {"enabled":True,"attributes":{},"redirectUris":[],"clientId":"dc","protocol":"openid-connect", "directAccessGrantsEnabled":True}
        clients = self.kc.build('clients', realm)
        if not clients.create(client).isOk(): 
            raise Exception('Cannot create Client')

    def createUsers(self):
        realm = self.realm
        test_users = [
                {"enabled":'true',"attributes":{},"username":"batman","firstName":"Bruce", "lastName":"Wayne", "emailVerified":""}, 
                {"enabled":'true',"attributes":{},"username":"superman","firstName":"Clark", "lastName":"Kent", "emailVerified":""}, 
                {"enabled":'true',"attributes":{},"username":"aquaman","firstName":"AAA%", "lastName":"Corrupt", "emailVerified":""}
        ]

        users = self.kc.build('users', realm)
        
        for usr in test_users: 
            users.create(usr).isOk()



    def goodBye(self): 
        remove_state = self.master_realm.remove(self.realm)


    def getKeycloak(self):
        return self.kc
