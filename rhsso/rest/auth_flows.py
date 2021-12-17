from .crud import KeycloakCRUD
from .helper import ValidateParams
import requests, json

def patchCreate(obj, resource): 
    mutated = obj.extend([resource])
    obj.create = lambda payload: mutated.create(payload)

    return obj



class AuthenticationFlows(KeycloakCRUD):
    def __init__(self, url, token): 
        super().__init__(url, token)
        
        #/authentication/flows, is the real root URL for this functionality.
        self.addResources(['flows'])

    def __addChild(self, executionType, authFlow):
        alias = authFlow['alias']
        ret_obj = super().extend([alias, 'executions'])

        return patchCreate(ret_obj, authFlow) 

    # Generate a CRUD object pointing to /realm/<realm>/authentication/alias/executions/flow
    def subFlowFor(self, authFlow):
        return self.__addChild('flow', authFlow)

    # Generate a CRUD object pointing to /realm/<realm>/authentication/alias/executions/executions
    def executionFor(self, authFlow):
        return self.__addChild('execution', authFlow)

