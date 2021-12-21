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
#

def FlowBuilder(token, kcAPI, parentFlow):
    parentFlowAlias = parentFlow['alias']
    flow = KeycloakCRUD(token = token, KeycloakAPI=kcAPI)
    flow.addResourcesFor('create',[parentFlowAlias, 'executions', 'flow'])
    flow.addResourcesFor('read',[parentFlowAlias, 'executions'])

    deleteMethod = flow.getMethod('delete')
    deleteMethod.replaceResource('flows', 'executions')

    return flow
    
def ExecutionBuilder(token, kcAPI, parentFlow):
    parentFlowAlias = parentFlow['alias']
    flow = KeycloakCRUD(token = token, KeycloakAPI=kcAPI)
    flow.addResourcesFor('create',[parentFlowAlias, 'executions', 'execution'])
    flow.addResourcesFor('read',[parentFlowAlias, 'executions'])

    deleteMethod = flow.getMethod('delete')
    deleteMethod.replaceResource('flows', 'executions')

    return flow
 
class AuthenticationFlows(KeycloakCRUD):
    def __init__(self, url, token): 
        super().__init__(url, token)
        self.addResources(['flows'])

    # Generate a CRUD object pointing to /realm/<realm>/authentication/flow_alias/executions/flow
    def flows(self, authFlow):
        return FlowBuilder( 
                token=self.token, 
                kcAPI=self, 
                parentFlow=authFlow)

    # Generate a CRUD object pointing to /realm/<realm>/authentication/flow_alias/executions/execution
    def executions(self, authFlow):
        return ExecutionBuilder( 
                token=self.token, 
                kcAPI=self, 
                parentFlow=authFlow)


