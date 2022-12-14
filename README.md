# Keycloak API

Python module to automate Keycloak or Red Hat Single Sign-On (RHSSO) configuration.

## How To Install

```sh
pip install kcapi
```


## Testing

### Start test server

To run the test you would need a Keycloak instance, you can run one locally or in the [cloud]( https://developers.redhat.com/developer-sandbox/get-started) then you just have to follow this steps: 

To start a Keycloak instance in docker container use command like below.
In this case TLS certificate verification needs to be disabled for testing.

```shell
# keycloak:15.0.2 is close to RedHat SSO 7.5
# keycloak:9.0.3 is close to RedHat SSO 7.4
docker run -d -p 8080:80 -p 8443:443 -e KEYCLOAK_USER=admin -e KEYCLOAK_PASSWORD=admin quay.io/keycloak/keycloak:15.0.2
```

You can also use RedHat SSO container.
At [sso75-openshift-rhel8](https://catalog.redhat.com/software/containers/rh-sso-7/sso75-openshift-rhel8/611418806e1e42ca4d6decf1) are instructions for RH SSH 7.5.

```shell
docker login registry.redhat.io
Username: {REGISTRY-SERVICE-ACCOUNT-USERNAME}
Password: {REGISTRY-SERVICE-ACCOUNT-PASSWORD}
docker pull registry.redhat.io/rh-sso-7/sso75-openshift-rhel8:7.5-35

docker run --name rhsso -it -p 8080:8080 -p 8443:443 -e SSO_ADMIN_USERNAME=admin -e SSO_ADMIN_PASSWORD=admin -it registry.redhat.io/rh-sso-7/sso75-openshift-rhel8:7.5-35
# By default, no https for API calls.
# Web GUI seems to be disabled.
export KC_ENDPOINT=https://172.17.0.2:8080
```

### Run tests

With Keycloak instance running we can start tests:

```shell script
python3.10 -m venv .venv
source .venv/bin/activate
pip install requests
pip install -e .

# Setup SSO server - go to https://developers.redhat.com/developer-sandbox/get-started,
# launch sandbox environment, +Add, select some "Red Hat Single Sign-On..." template.
export KC_ENDPOINT=https://my-first-sso-me-me-dev.apps.sandbox.x8i5.p1.openshiftapps.com
# Or use local docker container, with self-signed TLS server certificate
export KEYCLOAK_API_CA_BUNDLE=
export KC_ENDPOINT=https://172.17.0.2:8443

export KC_USER=admin
export KC_PASSWORD=admin_password
export KC_REALM=myrealm  # do not use master realm, it cannot be removed

# unittests are faster with prerecorded http requests
# See https://vcrpy.readthedocs.io/en/latest/usage.html#record-modes.
# export VCRPY_RECORD_MODE=none  # this is default
# To re-recored VCR cassettes:
# export VCRPY_RECORD_MODE=all

python -m unittest
```

## Optionally disable TLS certificate verification

Environment variable `KEYCLOAK_API_CA_BUNDLE` can be used to disable TLS certificate verification.
`KEYCLOAK_API_CA_BUNDLE` can have 3 different values:
- unset (default) - TLS verification is enforced
- empty string - TLS verification is disabled
- path to file or directory
  - file contains a CA certificate bundle or,
  - directory contains individual CA certificate files.

## Build package locally

```shell script
pip install -r requirements-dev.txt
python -m build
# optionally upload to test.pypi.org
TWINE_USERNAME=__token__ TWINE_PASSWORD=$MY_TOKEN python3 -m twine upload --repository testpypi dist/*
```

## API

### OpenID

This class provides takes care of OpenID login using [password owner credentials](https://datatracker.ietf.org/doc/html/rfc6749#section-1.3.3) flow.


#### Constructor

```python
from rhsso import OpenID

oid_client = OpenID({
        "client_id": "admin-cli",
        "username": USER,
        "password": PASSWORD,
        "grant_type":"password",
        "realm" : "master"
        }, endpoint)
```

- **client_id**: Client Identifier in Keycloak.
- **username**: Login username for the Realm.
- **password**: Login password for the Realm.
- **grant_type**: The grant type you want to use (usually ``password``).
- **endpoint**: A Keycloak or RHSSO URL endpoint, something like: ``https://my_keycloak.com``.  


#### Methods

##### getToken

This will initiate a session with the Keycloak server and will return a OpenID token back.

```python
oid_client.getToken() #glTeDLlmmpLYoAAUMcFQqNOMjw5dA
```

##### createAdminClient

This is a shortcut static method in order to get an admin token from Keycloak.

```python
    oidc = OpenID.createAdminClient(self.USER, self.PASSWORD)
    oidc.getToken() #glTeDLlmmpLYoAAUMcFQqNOMjw5dA
```
### Keycloak

This class builds all the Keycloak configuration REST resources by using REST conventions we can target the majority of Keycloak services.

#### Constructor

```Python
kc = Keycloak(token, self.ENDPOINT)
```

The constructor takes two parameters:

- **token**: A token with enough priviledge to perform the desired operation.
- **endpoint**: A Keycloak or RHSSO URL endpoint, something like: ``https://my_keycloak.com``.  


#### Methods

#### build
This methods build a REST client (capabilities detailed below) targeting a specific Keycloak REST resource.

```python
groups = kc.build('groups', 'my_realm')

# Create a group called DC
state = groups.create({"name": "DC"}).isOk()

```
> In this example we build the 'groups' API for ``my_realm`` Realm.

##### Supported Resources

Here is a quick list of supported resources:

- **users**:  [users API](https://access.redhat.com/webassets/avalon/d/red-hat-single-sign-on/version-7.0.0/restapi/#_create_a_new_user).
- **clients**: [client API](https://access.redhat.com/webassets/avalon/d/red-hat-single-sign-on/version-7.0.0/restapi/#_create_a_new_client).  
- **groups**:  [groups API](https://access.redhat.com/documentation/en-us/red_hat_single_sign-on/7.0/html/server_administration_guide/groups).
- **roles**: [roles API](https://access.redhat.com/webassets/avalon/d/red-hat-single-sign-on/version-7.0.0/restapi/#_create_a_new_role_for_the_realm_or_client_2)
- **identity-provider**: [identity provider API](https://access.redhat.com/webassets/avalon/d/red-hat-single-sign-on/version-7.0.0/restapi/#_get_identity_providers)


> As long as you find a REST endpoint that follow the standard you can use this method to build a client around it, an example of this is the non well documented ``components`` endpoint.

- **components**: This API allows you configure things like [user federation](https://access.redhat.com/documentation/en-us/red_hat_single_sign-on/7.0/html/server_administration_guide/user-storage-federation) or [Realm keys](https://access.redhat.com/documentation/en-us/red_hat_single_sign-on/7.2/html/server_administration_guide/admin_permissions#realm_keys).

- **authentication**: Provide access to built-in and/or custom authentication flows.
<BR>

#### admin
Similar to the ``build`` method but the client points to the ``master`` realm, allowing us operation such as realm creation.

```python
    main_realm = kc.admin()

    # Creates a realm called my_realm
    main_realm.create({"enabled": "true", "id": my_realm, "realm": my_realm})
```


### REST API

When you use the ``build`` or ``admin`` methods you will get back a **REST** class pointing to the Keycloak resource, keep in mind that this class don't check that the resource is valid, this is done to keep it flexible and to make it easy to adapt to new Keycloak REST API changes in the future.  

#### Usage

In order to create one you need to ``build`` method we have used before:

```python
batman = {
    "enabled":'true',
    "attributes":{},
    "username":"batman",
    "firstName":"Bruce",
    "lastName":"Wayne",
    "emailVerified":""
}

users = kc.build('users', 'DC')

# Create a user called batman in DC
state = users.create(batman).isOk()
```

#### Methods

Following the example above lets see the methods we have starting with the usual CRUD methods:

#### create

This method ``POST`` a dictionary into any given resource:

```python
batman = {
    "enabled":'true',
    "attributes":{},
    "username":"batman",
    "firstName":"Bruce",
    "lastName":"Wayne",
    "emailVerified":""
}

state = users.create(batman).isOk()
```

- **dictionary**: Dictionary with the fields we want to POST to the server.




#### update

This method performs a ``PUT`` on the resource.

```python
batman_update = {
    "firstName":"Bruno",
    "emailVerified": True
}

id = 'bf81a9d9-811f-4807-bd69-3d74eecbe9f4'

state = users.update(id, batman_update).isOk()
```
- **id**: Id of the resource in Keycloak.
- **dictionary**: Dictionary representing the updated fields.  

#### remove
This method sends a ``DELETE`` to the pointed resource.

```python
batman_update = {
    "firstName":"Bruno",
    "emailVerified": True
}

id = 'bf81a9d9-811f-4807-bd69-3d74eecbe9f4'

state = users.remove(id).isOk()
```
- **id**: Id of the resource in Keycloak.
- **dictionary**: Dictionary representing the updated fields.  


#### get
Send a ``GET`` request to retrieve a specific Keycloak resource.

```python
id = 'bf81a9d9-811f-4807-bd69-3d74eecbe9f4'

user = users.get(id).response()
```

#### all

Return all objects of a particular resource type.

```Python
users = kc.build('users', 'DC')

# Create a user called batman in DC
user_list = users.all() # [ {id:'xxx-yyy', username: 'batman', ...} ]   
```
#### findFirst
Finds a resource by passing an arbitrary key/value pair.

```Python
users = kc.build('users', 'DC')

users.findFirst({"key":"username", "value": 'batman'})
```

#### exist
Check if a resource matching the provided ``id`` exists:
```Python
users = kc.build('users', 'DC')
id = 'bf81a9d9-811f-4807-bd69-3d74eecbe9f4'

users.exists(id) #True
```

#### existByKV
Check if a resource matching the provided key/value pair, exists.


```Python
users = kc.build('users', 'DC')

users.existByKV({"key":"username", "value": 'batman'}) #False
```


### ResponseHandler

Each **CRUD** method returns a ``ResponseHandler`` class with the following methods.

#### Methods


#### response
returns the requests [response object](https://docs.python-requests.org/en/latest/api/#requests.Response).

```Python
users.update(id, batman_update).response().status_code #HTTP 201
```


#### isOk

Return ``True`` if the request complete  successfully otherwise it will raise an exception.

```Python
state = users.update(id, batman_update).isOk() # Return True here.
```

#### verify

Does the same as ``isOk`` but it allow you to chain more methods.

```python
batman_update = {
    "firstName":"Bruno",
    "emailVerified": True
}

id = 'bf81a9d9-811f-4807-bd69-3d74eecbe9f4'

cookies = users.update(id, batman_update).verify().response().cookies # Get cookies.
```


## Specialisations

### Realms 

### KeycloakCaches 

This class handles the Keycloak caches. 

#### Instantiation 

```python
# Creates a REST API instance target the Realms API. 
realms = kc.build('realms', 'my_realm') 

# Gets the cache Realms cache API. 
caches = realms.caches(self.REALM)
```

#### clearUserCache 
This method tells Keycloak to clear the user cache.

```python
caches.clearUserCache()
```


#### clearRealmCache 
This method tells Keycloak to clear the realm cache.

```python
caches.clearRealmCache()
```


#### clearKeyCache 
This method tells Keycloak to clear the external public key cache for clients and identity providers.

```python
caches.clearKeyCache()
```

> For more information on how this caches works follow this [link](https://access.redhat.com/documentation/en-us/red_hat_single_sign-on/7.0/html/server_installation_and_configuration_guide/server_cache_configuration).


### Users

#### updateCredentials

Update user credentials.

```js
user_credentials = {
          'temporary': False,
          'value':'12345'
}

state = users.updateCredentials(user_info, user_credentials).isOk() # Updated user password.
```
Where:
- **temporary**: Boolean where if ``True`` provide a temporary password just for the first login.  
- **value**: String with the password.


#### joinGroup

Add a user into a existing [group](https://access.redhat.com/documentation/en-us/red_hat_single_sign-on/7.0/html/server_administration_guide/groups).

First we need a group:
```python
def createDCGroup():
  group = kc.build('groups', 'heroes')
  return group.create({"name": "DC"}).isOk()
```

Then we can join the group the following way:

```python
  createDCGroup()

  users = kc.build('users', 'heroes')
  user = {"key": "username", "value": "batman"}
  group = {"key": "name", "value": "DC"}

  users.joinGroup(user, group).isOk()
```

> The API works by matching the first occurrence between the provided ``key/value`` for the two resources (User and Group), this can help in various situation for example if we want to target the user by ``uuid``.


Using ``uuid`` as user identifier.

```python
  createDCGroup()

  users = kc.build('users', 'heroes')
  user = {"key": "uuid", "value": "23e4567-e89b-..."}
  group = {"key": "name", "value": "DC"}

  users.joinGroup(user, group).isOk()
```

Or we want to use the group ``id``:

```python
  user = {"key": "uuid", "value": "23e4567-e89b-..."}
  group = {"key": "id", "value": "f8d91722-a1f0-45e..."}

  users.joinGroup(user, group).isOk()
```
> If the field criteria don't return a unique value, the first entry in the list will be used.
#### leaveGroup

Remove a user from a group.

```python
  createDCGroup()

  users = kc.build('users', 'heroes')
  user = {"key": "username", "value": "batman"}
  group = {"key": "uuid", "value": "123e4567-e89b-..."}

  users.leaveGroup(user, group).isOk()

  user = {"key": "uuid", "value": "12d3-a456-4"}
  group = {"key": "id", "value": "123e4567-e89b-..."}

  users.leaveGroup(user, group).isOk()

```

> The same rules for ``key/value`` discussed above also applies here.


### Groups

To manage the relationship between realm level [roles](keycloak.org/docs/latest/server_admin/#assigning-permissions-and-access-using-roles-and-groups) and groups, we can use the **RealmsRolesMapping**.

To get an instance of this class you need to instantiate the ``group`` resource class:

```Python
groups = kc.build('groups', 'heroes')
```

And use the method ``realmRoles`` passing a valid [group dictionary](https://access.redhat.com/webassets/avalon/d/red-hat-single-sign-on/version-7.0.0/restapi/#_grouprepresentation):

```python
realmsRoles = groups.realmRoles({"key":"name", "value":'DC'})
```

Then we get a class with following methods:

#### add

Add a list of existing roles to a group.

```python
def makeRoles(self):
    roles = kc.build('roles', self.realm)
    lvl1 = roles.create({"name": "level-1"}).isOk()
    lvl2 = roles.create({"name": "level-2"}).isOk()
    return lvl1 and lvl2


if makeRoles():
  realmsRoles = groups.realmRoles({"key":"name", "value":'DC'})
  realmsRoles.add(["level-1", "level-2"])
```

#### remove
Remove a list of associated roles from a group.

```python
realmsRoles = groups.realmRoles({"key":"name", "value":'DC'})
realmsRoles.remove(["level-1", "level-2"])
```


