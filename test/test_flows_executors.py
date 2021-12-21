import unittest, time
from rhsso import OpenID, RestURL
from .testbed import TestBed 
import json
import time

USER = 'batman'
PASSWORD = '1234'

ADMIN_USER = "admin"
ADMIN_PSW  = "admin1234"
REALM = "test_heroes_test"
ENDPOINT = 'https://sso-cvaldezr-stage.apps.sandbox-m2.ll9k.p1.openshiftapps.com'

def create_testing_flows(flows, authenticationFlow):
        for flow in flows:
            state = authenticationFlow.create(flow)
 

class Testing_Authentication_Flows_API(unittest.TestCase):
    def test_flow_api_instantiantion(self):
        flows = self.authenticationFlow.all()
        self.assertTrue(len(flows) > 0)

    def testing_create_a_new_flow(self): 

        basic_flow = {
                "alias":"basic",
                "providerId":"basic-flow",
                "description":"my_new_basic_flow",
                "topLevel":True,
                "builtIn":False
                }
        
        client_flow = {
                "alias":"client",
                "providerId":"client-flow",
                "description":"my_new_client_flow",
                "topLevel":True,
                "builtIn":False
                }

        flows = [basic_flow, client_flow]

        for flow in flows:
            state = self.authenticationFlow.create(flow)
            self.assertTrue(state)

            rows = self.authenticationFlow.findFirst({"key":"alias", "value": flow['alias']})
            self.assertEqual(rows['alias'], flow['alias'])
            self.assertEqual(rows['providerId'], flow['providerId'])

    def testing_nested_flows(self): 
        basic_flow = self.flows[0]
        nestedFlow = {"alias":"_11111_","type":"basic-flow","description":"11111111","provider":"registration-page-form"}
        nestedExecution = {"provider":"auth-x509-client-username-form"} 

        flows = self.authenticationFlow.flows(basic_flow)
        flows.create(nestedFlow)

        nested_flows = flows.all()
        self.assertTrue(len(nested_flows) > 0)

        flw = nested_flows[0]
        self.assertEqual(nestedFlow["alias"],flw["displayName"])

        executions = self.authenticationFlow.executions(basic_flow)
        executions.create(nestedExecution)
        executions.create(nestedExecution)

        x509 = executions.findFirstByKV('displayName', 'X509/Validate Username Form')

        self.assertIsNotNone(x509)
        self.assertTrue(len( flows.all() ) == 3)
        self.assertTrue(len( executions.all() ) == 3)



    def testing_remove_executions_flows(self): 
        client_flow = self.flows[1]
        nestedExecution = {"provider":"client-x509"} 
        execs = self.authenticationFlow.executions(client_flow)
        state = execs.create(nestedExecution)
        state = execs.create(nestedExecution)

        self.assertTrue(len( execs.all() ) == 2)

        execs.removeFirstByKV('providerId', 'client-x509')

        self.assertTrue(len( execs.all() ) == 1)
        
        execs.removeFirstByKV('providerId', 'client-x509')

        self.assertTrue(len( execs.all() ) == 0)

    def testing_remove_nested_flows(self): 
        basic_flow = self.flows[2]
        nf1 = {"alias":"_00000_","type":"basic-flow","description":"11111111","provider":"registration-page-form"}
        nf2 = {"alias":"_22222_","type":"basic-flow","description":"22222222","provider":"registration-page-form"}

        flows = self.authenticationFlow.flows(basic_flow)
        state1 = flows.create(nf1)
        state2 = flows.create(nf2)

        self.assertTrue((state1 and state2))
        
        flows_list = flows.all()

        self.assertTrue(len(flows_list) == 2)
        flows.removeFirstByKV('displayName', nf1['alias'])
        flows_list = flows.all()
        self.assertTrue(len(flows_list) == 1)
        self.assertEqual(flows_list[0]['displayName'], nf2['alias'])

     

    @classmethod
    def setUpClass(self):
        self.testbed = TestBed(REALM, ADMIN_USER, ADMIN_PSW, ENDPOINT)
        self.testbed.createRealms()
        self.testbed.createUsers()
        self.testbed.createClients()
        self.authenticationFlow = self.testbed.getKeycloak().build('authentication', REALM)

        basic_flow = {
                "alias":"my_new_basic_flow",
                "providerId":"basic-flow",
                "description":"my_new_basic_flow",
                "topLevel":True,
                "builtIn":False
        }
        
        client_flow = {
                "alias":"my_new_client_flow",
                "providerId":"client-flow",
                "description":"my_new_client_flow",
                "topLevel":True,
                "builtIn":False
        }

        basic_flow_2 = {
                "alias":"my_new_basic_flow_2",
                "providerId":"basic-flow",
                "description":"my_new_basic_flow",
                "topLevel":True,
                "builtIn":False
        }
        
        self.flows = [basic_flow, client_flow, basic_flow_2]
        create_testing_flows(self.flows, self.authenticationFlow)

        
    @classmethod
    def tearDownClass(self):
        self.testbed.goodBye()
      
if __name__ == '__main__':
    unittest.main()
