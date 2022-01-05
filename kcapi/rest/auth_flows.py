from .crud import KeycloakCRUD
from .helper import ValidateParams
from .url import RestURL
import requests, json

# The keycloak API is a bit crazy here they add with: 
# Post /parentId/executions/execution 
# 
# But they delete with: 
#
# DELETE /executions/<id>
#
# Sadly we need to customize the URL's in order to make it work.
#


def make_flow(flow):
    alias = flow['displayName'] 
    provider = 'registration-page-flow' if not flow['providerId'] else flow['providerid'] 
    flow_type = 'basic-flow' if not flow['providerId'] else 'form-flow' 

    flow = {
            "alias":alias,
            "type": flow_type,
            "description":"empty", # WARN: This value is not validated in Keycloak, it can cause 500.
            "provider": provider,
    }

    return flow 


def make_execution(execution):
    provider = execution['providerId'] 
            
    return {'provider': provider} 


def isAuthenticationFlow(body): 
    return 'authenticationFlow' in body 


def publish(flow, api):
    if isAuthenticationFlow(flow):
        api.flows(root).create(make_flow(flow))
    else:
        api.executions(root).create(make_execution(flow))




def BuildAction(kcCRUD, parentFlow, actionType):
    parentFlowAlias = parentFlow['alias']
    kcCRUD.addResourcesFor('create',[parentFlowAlias, 'executions', actionType])
    kcCRUD.addResourcesFor('update',[parentFlowAlias, 'executions'])
    kcCRUD.addResourcesFor('read',[parentFlowAlias, 'executions'])

    deleteMethod = kcCRUD.getMethod('delete')
    deleteMethod.replaceResource('flows', 'executions')

    return kcCRUD


class AuthenticationFlows(KeycloakCRUD):
    def __init__(self, url, token): 
        super().__init__(url, token)
        self.addResources(['flows'])

    # Generate a CRUD object pointing to /realm/<realm>/authentication/flow_alias/executions/flow
    def flows(self, authFlow):
        flow = KeycloakCRUD(token = self.token, KeycloakAPI=self)

        return BuildAction( 
                kcCRUD=flow, 
                parentFlow=authFlow,
                actionType='flow')

    # Generate a CRUD object pointing to /realm/<realm>/authentication/flow_alias/executions/execution
    def executions(self, execution):
        flow = KeycloakCRUD(token = self.token, KeycloakAPI=self)

        return BuildAction( 
                kcCRUD=flow, 
                parentFlow=execution,
                actionType='execution')


'''

    def import(rootFlow, flows):  
        if not isinstance(flows, list):  
            raise Exception("Bad Parameters for Authentication Flow: auth_flow parameter should be an array.")

        root = rootFlow
        currentLevel = 0
        
        for flow in flows:
            publish(flow, self) 
            currentLevel += 1
             


'''
            





