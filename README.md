# DBAC

DBAC stands for Directory-Based Access Control. It combines distributed IoT directories and attribute-based access control.

## History

This directory application used to be named as "Droit". Therefore, the term "Droit" may appear in the source codes to refer to a directory.  

## To bootstrap the project

1. `git clone https://github.com/Halleloya/DABAC.git`.
2. Install dependencies `pip install -r requirements.txt`. (Note: you might want to have a virtual environment, in case any potential package conflict)
3. Configure the database, e.g., store your database in data/db (create a folder for it if it doesn't exist), and `mongod --dbpath data/db`. 
4. Run the shell `python runall.py` or `./run.sh` to run all levels of the directory. It create a simple tree-like topology for the geographically distributed directories. 

Sidenotes:

To run a local directory in the current structure `python run.py --level [level name]`. Try `python run.py --help` for more information. 

To run a single directory `python -m Droit.run`. It is easy and basically enough to test basic functions.

Please note that you are supposed to change the [ip] and [port] manually in the `config.py` file, if needed. 

To disable InsecureTransportError of OAuth2 (as https is required, but run with http in localhost when starting the third-party services): add `export OAUTHLIB_INSECURE_TRANSPORT=1` and `export AUTHLIB_INSECURE_TRANSPORT=1` to your env/bin/activate, or just input this command everytime restart the virtual environment. Please be noted that you should never do that in your production. 


## A sample walk-through 

Below we show a sample walk-through with a binary tree-like structure. By default (only for demo), directories are geographically distributed and connected with each other as this topology. 

```
level1 (master)
level2a level2b
level3aa level3ab level3ba level3bb
level4aaa level4aab level4aba level4abb level4baa level4bab level4bba level4bbb  
level5aaaa level5aaab ...
level6aaaaa level6aaaab ...
```

## Settings

By default, all the directoires run on localhost. The tree-like structure starts from port 5001, with the name of level1 (also called master directory or root directory). The single directory module named SingleDirectory runs on port 4999.

MongoDB runs on its default port 27017. To run MongoDB on another port: add `--port [port]` when starting the database, and change the configure files to direct apps to database. 

To release all the ports occupied by directories: `sudo kill -9 $(lsof -i:5001 -i:5002 -i:5003 -i:5004 -i:5005 -i:5006 -i:5007 -i:5008 -t)`.


## Authentication

We utilize OpenID library to implement a federated identtiy assertion model among directories. In general, one directory can rely on its counterparts to authenticate a user after some configurations. From a user's perspective, one can sign in a directory with the identity from another directory. 

### Example 
To illustrate how to configure it, we give an example that level3aa provides a means of login with identity of level2b. In this example, level2b is the OIDC provider, while level3aa is the OIDC client.

> In level2b (http://localhost:5003/auth/oauth_list), register a new client. The only nonintuitive field is "Redirect URI", which is the address that the provider should redirect back to the client. In the example, it should be `http://localhost:5004/auth/oidc_auth_code/level2b`.

> In level3aa's backend configuration (Droit/auth/providers_config.py), change the providers_config with the client's id and secret specified in the known OIDC clients of level2b.

```
"level3aa": {
        "level2b": {
            "client_id": 'sQDK1uX1R62sZf3f9AB0eTJb',
            "client_secret": 'pkcqeqvYvzKE1zHjhRv30MFVcIDve6b4tZRmmjGf68M0ZmoK',
            "access_token_url": 'http://localhost:5003/auth/oidc_token',
            "access_token_params": None,
            "authorize_url": 'http://localhost:5003/auth/oidc_authorize',
            "authorize_params": None,
            "api_base_url": 'http://localhost:5003/api',
            "client_kwargs": {
                'scope': 'openid profile',
                'token_endpoint_auth_method': 'client_secret_basic'}
        }
    }
```

> Now you can login level3aa with your username and password in level2b.




## Attribute Based Access Control (ABAC)
The ABAC system can be used to specify in what conditions a thing can be accessed. Access rules are specified as policies, and requests are automatically generated when users request through the provided interfaces. Details about policy formats can be found from the py_abac library. By default, requests are denied if there are no policies associated. When there is a conflict, the policy with highest priority dominates. 


## Attribute Authorization System
The attribute authorization system can be used to retrieve attribute information from various resource providers. The authorization process is triggered by the "Authorize" button under "Attributes". The system identities and classifies the attributes required by the associated policies in the IoT directory. The user will be redirected to the user consent page, where they can choose the attribute what they allow the ABAC system to access. The authorization and data retrieval process can be done iteratively.

Currently, the system supports three basic types of attributes and assumes their sources: subject (user) attributes (from OIDC provider), object attributes (from TDs), and environmental attributes (from a third-party server). Sample ABAC policies are in `/ABAC` folder (json files).

### Third-party
"third-party" is a sample resource provider, which conveys a vision that some attributes are provided by other servers. For demo use, it contains any information through third-parties (e.g., weather information including temperature and rainfall). The configuration for the OAuth client is stored in "Droit/auth/providers_config.py". Run the sample server by `python app.py` in the "third-party" directory. To test the policy which require attributes from third parties, you should ensure that the current user (e.g., "test_user") has such attributes in the database (manually insert before access).  The sample server runs on port 5100, and you will need to manually input the values (username, weather, rainfall) to the third-party database. 

To test the third-party logic, we need some sort of manually inputs. 
redirect uri: `http://localhost:5004/auth/info_authorize`. allowed scope: `weather`. allowed grant type: `authorization_code`. allowed response type: `code`. After generating the client, put the client info to the "Droit/auth/providers_config.py".


## Go deeper in ABAC
To test the following features, please refer to the ABAC/Spring2021/README.md file.

1) Geolocation based authorization.
2) Dynamic attributes based authorization.
3) Aggregate query.
4) MQTT Notification system.

## Acknowledgement
We would like to thank Yifan, Vibhas, Andrea for their valuable inputs and contributions on the implementation of this prototype. 
