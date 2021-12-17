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

class Testing_Authentication_Flows_API(unittest.TestCase):
    def test_flow_api_instantiantion(self):
        flows = self.auth_flows.all()
        self.assertTrue(len(flows) > 0)

    def test_create_a_new_flow(self): 
        for flow in self.flows:
            state = self.auth_flows.create(flow)
            self.assertTrue(state)

            rows = self.auth_flows.findFirst({"key":"alias", "value": flow['alias']})
            self.assertEqual(rows['alias'], flow['alias'])
            self.assertEqual(rows['providerId'], flow['providerId'])

    def test_create_a_nested_flow_inside_basic_flow(self): 
        basic_flow = self.flows[0]

        executionStep = {"provider":"no-cookie-redirect"}
        execsSteps = self.auth_flows.executionFor(basic_flow)
        state = execsSteps.create(executionStep)
        self.assertTrue(state)

        nestedFlow = {"alias":"_11111_","type":"basic-flow","description":"11111111","provider":"registration-page-form"}

        state = self.auth_flows.subFlowFor(basic_flow).create(nestedFlow)
        self.assertTrue(state)

    def testing_getting_executions_in_a_flow(self):
        basic_flow = self.flows[0]
        execsSteps = self.auth_flows.executionFor(basic_flow)

        execs = execsSteps.all() 
        print("oooo: ", execs)

    def test_add_execution_to_flow_YYYY(self):
        basic_flow = self.flows[0]
        execsSteps = self.auth_flows.executionFor(basic_flow)

        execs = execsSteps.all() 
        print("execs 22: ", execs)



    def test_add_fuck_you(self):
        basic_flow = self.flows[0]
        execsSteps = self.auth_flows.executionFor(basic_flow)

        execs = execsSteps.all() 
        print("execs 22: ", execs)



    def testing_getting_executions_in_a_flow_222(self):
        basic_flow = self.flows[0]

        executionStep = {"provider":"no-cookie-redirect"}
        execsSteps = self.auth_flows.executionFor(basic_flow)
        state = execsSteps.create(executionStep)
        self.assertTrue(state)

        execsSteps = self.auth_flows.executionFor(basic_flow)

        execs = execsSteps.all() 
        print("yyyyy: ", execs)




    @classmethod
    def setUpClass(self):
        self.testbed = TestBed(REALM, ADMIN_USER, ADMIN_PSW, ENDPOINT)
        self.testbed.createRealms()
        self.testbed.createUsers()
        self.testbed.createClients()
        self.auth_flows = self.testbed.getKeycloak().build('authentication', REALM)

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

        
        self.flows = [basic_flow, client_flow]
        
    @classmethod
    def tearDownClass(self):
        self.testbed.goodBye()
        print('do Nothing')

if __name__ == '__main__':
    unittest.main()
