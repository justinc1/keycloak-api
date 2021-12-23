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

def BuildAction(kcCRUD, parentFlow, actionType):
    parentFlowAlias = parentFlow['alias']
    kcCRUD.addResourcesFor('create',[parentFlowAlias, 'executions', actionType])
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
    def executions(self, authFlow):
        flow = KeycloakCRUD(token = self.token, KeycloakAPI=self)

        return BuildAction( 
                kcCRUD=flow, 
                parentFlow=authFlow,
                actionType='execution')


