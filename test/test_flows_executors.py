import unittest, time
from rhsso import OpenID, RestURL
from .testbed import TestBed 
import json
import time

def create_testing_flows(flows, authenticationFlow):
        for flow in flows:
            state = authenticationFlow.create(flow)

def new_flow_definition(name):
    flow = {"alias":name,"type":"basic-flow","description":"testing","provider":"registration-page-form"}
    return dict(flow) 
        
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
        name = '--yyyyyyy---'
        nestedFlow = new_flow_definition(name) 
        nestedExecution = {"provider":"auth-x509-client-username-form"} 

        flows = self.authenticationFlow.flows(basic_flow)
        resp = flows.create(nestedFlow)
        self.assertTrue(resp.isOk())

        nested_flows = flows.all()
        self.assertTrue(len(nested_flows) > 0)

        flw = nested_flows[0]
        self.assertEqual(nestedFlow["alias"],flw["displayName"])

        executions = self.authenticationFlow.executions(basic_flow)
        executions.create(nestedExecution)
        executions.create(nestedExecution)

        x509 = executions.findFirstByKV('displayName', 'X509/Validate Username Form')

        self.assertIsNotNone(x509)
        flow_size = len( flows.all() )
        self.assertEqual(flow_size, 3)
        
        execs_size = len( executions.all() )
        self.assertEqual(execs_size, 3)


    def testing_flows_inside_flows(self):
        parent_flow = self.flows[3]
        x1_def = new_flow_definition('x1') 
        x12_def = new_flow_definition('x12') 
        x123_def = new_flow_definition('x123') 
        
        #Top node 
        #parent --> child x1 
        parent = self.authenticationFlow.flows(parent_flow)
        state = parent.create(x1_def).isOk()
        self.assertTrue(state)

        #Adding child
        #parent --> child x1 --> x12 
        x1 = self.authenticationFlow.flows(x1_def)
        state = x1.create(x12_def).isOk()
        self.assertTrue(state)

        #Adding nested child
        #parent --> child x1 --> x12 --> x123 
        x12 = self.authenticationFlow.flows(x12_def)
        state = x12.create(x123_def).isOk()
        self.assertTrue(state)
        
        #Adding a nested executor to the last node 
        #parent --> child x1 --> x12 --> x123  
        #                                 | 
        #                                 v 
        #                             client-x509
        x123 = self.authenticationFlow.executions(x123_def)
        execution = {"provider":"docker-http-basic-authenticator"} 
        state = x123.create(execution).isOk()
        self.assertTrue(state)


        executions = self.authenticationFlow.executions(parent_flow)
        exec_size = len( parent.all() )

        self.assertEqual(exec_size, 4)



    def testing_remove_executions_flows(self): 
        client_flow = self.flows[1]
        nestedExecution = {"provider":"client-x509"} 
        execs = self.authenticationFlow.executions(client_flow)

        resp = execs.create(nestedExecution)
        self.assertTrue(resp.isOk())
        
        resp = execs.create(nestedExecution)
        self.assertTrue(resp.isOk())

        elen = len( execs.all() )
        self.assertEqual(elen, 2)

        execs.removeFirstByKV('providerId', 'client-x509')

        elen = len( execs.all() )
        self.assertEqual(elen, 1)
        
        execs.removeFirstByKV('providerId', 'client-x509')

        elen = len( execs.all() )
        self.assertEqual(elen, 0)
        

    def testing_remove_nested_flows(self): 
        basic_flow = self.flows[2]
        nf1 = {"alias":"_aaaaaa_","type":"basic-flow","description":"11111111","provider":"registration-page-form"}
        nf2 = {"alias":"_bbbbbb_","type":"basic-flow","description":"22222222","provider":"registration-page-form"}

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
        self.testbed = TestBed()
        self.testbed.createRealms()
        self.testbed.createUsers()
        self.testbed.createClients()
        self.authenticationFlow = self.testbed.getKeycloak().build('authentication', self.testbed.REALM)

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
        
        flow_3 = {
                "alias":"_nested_",
                "providerId":"basic-flow",
                "description":"my_new_basic_flow",
                "topLevel":True,
                "builtIn":False
        }
        
        self.flows = [basic_flow, client_flow, basic_flow_2, flow_3 ]
        create_testing_flows(self.flows, self.authenticationFlow)

        
    @classmethod
    def tearDownClass(self):
        self.testbed.goodBye()
        return True
      
if __name__ == '__main__':
    unittest.main()
