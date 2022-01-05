# Keycloak API

Python module to automate Keycloak or Red Hat Single Sign-On (RHSSO) configuration.

## How To Install

```sh
pip install kcapi
```


## API

### OpenID

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
self.kc = Keycloak(token, self.ENDPOINT)
```

The constructor takes two parameters:

- **token**: A token with enough priviledge to perform the desired operation.
- **endpoint**: A Keycloak or RHSSO URL endpoint, something like: ``https://my_keycloak.com``.  


#### Methods

##### build
This methods build a REST client (capabilities detailed below) targeting a specific Keycloak REST resource.

```python
groups = self.kc.build('groups', 'my_realm')

# Create a group called DC
state = groups.create({"name": "DC"}).isOk()

```
> In this example we build the 'groups' API for ``my_realm`` Realm.

##### Supported Resources

Here is a quick list of supported resources:

- **groups**:  [groups API](https://access.redhat.com/documentation/en-us/red_hat_single_sign-on/7.0/html/server_administration_guide/groups).
- **users**:  [users API](https://access.redhat.com/webassets/avalon/d/red-hat-single-sign-on/version-7.0.0/restapi/#_create_a_new_user).
- **clients**: [client API](https://access.redhat.com/webassets/avalon/d/red-hat-single-sign-on/version-7.0.0/restapi/#_create_a_new_client).  
- **roles**: [roles API](https://access.redhat.com/webassets/avalon/d/red-hat-single-sign-on/version-7.0.0/restapi/#_create_a_new_role_for_the_realm_or_client_2)


> As long as you find a REST endpoint that follow the standard you can use this method to build a client around it, an example of this is the non well documented ``components`` endpoint.

- **components**: This API allows you configure things like [user federation](https://access.redhat.com/documentation/en-us/red_hat_single_sign-on/7.0/html/server_administration_guide/user-storage-federation) or [Realm keys](https://access.redhat.com/documentation/en-us/red_hat_single_sign-on/7.2/html/server_administration_guide/admin_permissions#realm_keys).



##### admin
Similar to the ``build`` method but the client points to the ``master`` realm, allowing us operation such as realm creation.

```python
    main_realm = self.kc.admin()

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

users = self.kc.build('users', 'DC')

# Create a user called batman in DC
state = users.create(batman).isOk()
```

#### Methods

Following the example above lets see the methods we have starting with the usual CRUD methods:

###### create

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

- - **dictionary**: Dictionary with the fields we want to POST to the server.




###### update

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

###### remove
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


###### get
Send a ``GET`` request to retrieve a specific Keycloak resource.

```python
id = 'bf81a9d9-811f-4807-bd69-3d74eecbe9f4'

user = users.get(id).response()
```

###### all

Return all objects of a particular resource type.

```Python
users = self.kc.build('users', 'DC')

# Create a user called batman in DC
user_list = users.all() # [ {id:'xxx-yyy', username: 'batman', ...} ]   
```
###### findFirst
Finds a resource by passing an arbitrary key/value pair.

```Python
users = self.kc.build('users', 'DC')

users.findFirst({"key":"username", "value": 'batman'})
```

###### exist
Check if a resource matching the provided ``id`` exists:
```Python
users = self.kc.build('users', 'DC')
id = 'bf81a9d9-811f-4807-bd69-3d74eecbe9f4'

users.exists(id) #True
```

###### existByKV
Check if a resource matching the provided key/value pair, exists.


```Python
users = self.kc.build('users', 'DC')

users.existByKV({"key":"username", "value": 'batman'}) #False
```


### ResponseHandler

Each **CRUD** method returns a ``ResponseHandler`` class with the following methods.

#### Methods


###### response
returns the requests [response object](https://docs.python-requests.org/en/latest/api/#requests.Response).

```Python
users.update(id, batman_update).response().status_code #HTTP 201
```


###### isOk

Return ``True`` if the request complete  successfully otherwise it will raise an exception.

```Python
state = users.update(id, batman_update).isOk() # Return True here.
```

###### verify

Does the same as ``isOk`` but it allow you to chain more methods.

```python
batman_update = {
    "firstName":"Bruno",
    "emailVerified": True
}

id = 'bf81a9d9-811f-4807-bd69-3d74eecbe9f4'

cookies = users.update(id, batman_update).verify().response().cookies # Get cookies.
```
