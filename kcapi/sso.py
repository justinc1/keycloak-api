from collections import namedtuple

from .rest.crud import KeycloakCRUD
from .rest.targets import Targets
from .rest.groups import Groups
from .rest.roles import RealmRoleCRUD, RolesURLBuilder
from .rest.users import Users
from .rest.realms import Realms, RealmURLBuilder
from .rest.url import RestURL
from .rest.idp import IdentityProviderURLBuilder
from .rest.auth_flows import AuthenticationFlows, AuthenticationFlowURLBuilder
from .rest.clients import Clients
from .rest.client_scopes import ClientScopeCRUD
from .rest.recovery import add_failiure_recovery_decorator

from .oid import get_well_known_info, Token

KCResourceTypes = {
    "users": Users,
    "groups": Groups,
    "realms": Realms,
    "authentication": AuthenticationFlows,
    "clients": Clients,
    "roles": RealmRoleCRUD,
    "client-scopes": ClientScopeCRUD,
}

URLBuilders = {
    'roles': RolesURLBuilder,
    'authentication': AuthenticationFlowURLBuilder,
    "idp": IdentityProviderURLBuilder,
    "identity-provider": IdentityProviderURLBuilder,
    "realms": RealmURLBuilder,
}


def GenericURLBuilder(url):
    targets = Targets.makeWithURL(url)
    return targets

def resource(resource_name=None, token=None):
    KCResourceAPI = KeycloakCRUD if not resource_name in KCResourceTypes else KCResourceTypes[resource_name]
    resource = KCResourceAPI()
    resource.token = token

    return resource

def configure_url(url=None, resource_name=None):
    URLBuilder = GenericURLBuilder if not resource_name in URLBuilders else URLBuilders[resource_name]
    return URLBuilder(str(url))


ServerInfo = namedtuple("ServerInfo", ["version", "profile_name"])


MASTER_REALM = 'master'
class Keycloak:
    @staticmethod
    def instantiate_with_refresh_token(url=None, refresh_token=None, client_id=None):
        well_known = get_well_known_info(url,MASTER_REALM)
        token = Token(well_known=well_known, refresh_token=refresh_token, client_id=client_id)
        token.client_id = token.client_id if not client_id else client_id
        return Keycloak(token=token, url=url)

    @staticmethod
    def instantiate_with_raw_json(url=None, json_string=None, client_id=None):
        well_known = get_well_known_info(url, MASTER_REALM)
        token = Token(well_known=well_known, raw_json_str=json_string, client_id=client_id)
        return Keycloak(token=token, url=url)

    def __init__(self, token=None, url=None):
        if not token:
            raise Exception("No authentication token provided.")

        if not url:
            raise Exception("No Keycloak endpoint URL has been provided.")

        self.token = token
        self.url = RestURL(url=url, resources=["auth", "admin", "realms"])
        self.url_serverinfo = RestURL(url=url, resources=["auth", "admin", "serverinfo"])
        self._server_info = None

    def admin(self):
        adm = resource(token=self.token)
        adm.targets = configure_url(url=self.url.copy())
        return add_failiure_recovery_decorator(adm)

    def build(self, resource_name, realm):
        url = self.url.copy()
        url.addResources([realm, resource_name])

        res = resource(token=self.token, resource_name=resource_name)
        res.targets = configure_url(url=url, resource_name=resource_name)
        return add_failiure_recovery_decorator(res)

    def build_serverinfo(self):
        # just copy-paste-change build(), we are interested in serverinfo only
        url = self.url_serverinfo.copy()

        res = resource(token=self.token, resource_name="")
        res.targets = configure_url(url=url, resource_name="")
        return add_failiure_recovery_decorator(res)

    @property
    def server_info(self):
        if self._server_info is None:
            serverinfo_api = self.build_serverinfo()
            serverinfo = serverinfo_api.get(None).verify().resp().json()
            self._server_info = ServerInfo(
                version=serverinfo["systemInfo"]["version"],
                profile_name=serverinfo["profileInfo"]["name"],
            )
            # Keycloak example return values:
            #   profile=community version=15.0.2
            # RedHat SSO example return values:
            #   profile=product version=7.5.2.GA

        return self._server_info

    def server_info_compound_profile_version(self, version_parts=2):
        # with version_parts=3 a string like "community 15.0" or "product 7.5" is returned
        compound_profile_version = self.server_info.profile_name + " "
        compound_profile_version += ".".join(self.server_info.version.split(".")[:version_parts])
        return compound_profile_version
