# DBAC

DBAC stands for Directory-Based Access Control. It combines distributed IoT directories and attribute-based access control. This project prototypes DBAC. 

Please cite the following paper if the project contributes to your work.

> Luoyao Hao, Vibhas Naik, and Henning Schulzrinne, "DBAC: Directory-Based Access Control for Geographically Distributed IoT Systems", IEEE International Conference on Computer Communications (INFOCOM), 2022.


## To Bootstrap the Project

1. Clone the project from this repository `git clone https://github.com/Halleloya/DBAC.git`.
2. Create a virtual environment (taking virtualenv as an example) `python3 -m venv env`, `source env/bin/activate`.
3. Install dependencies `pip3 install -r requirements.txt`. (Note: in the following we assume that you are using python3 and pip3.)
4. Configure the database, e.g., store your database in data/db (create a folder for it if it doesn't exist), and `mongod --dbpath data/db`. 
5. Open another terminal and go to the same virtual environment. Then, run the shell `python runall.py` or `./run.sh` to start all levels of the directory (i.e., a simple tree-like topology for the geographically distributed directories). 

Sidenotes:

To run a local directory in the current structure `python run.py --level [level name]`. Try `python run.py --help` for more information. 

To run a single directory `python -m Droit.run`. It is easy and basically enough to test directory functionalities.

Please note that you are supposed to change the [ip] and [port] manually in the `config.py` file, if needed. 

To disable InsecureTransportError of OAuth2 (as https is required, but run with http in localhost when starting the third-party services): add `export OAUTHLIB_INSECURE_TRANSPORT=1` and `export AUTHLIB_INSECURE_TRANSPORT=1` to your env/bin/activate, or just input this command everytime restart the virtual environment. Please be noted that you should never do that in your production. 

The directory application used to be named as "Droit (Directories for IoT)". Therefore, the term "Droit" may appear in the source codes to refer to a single directory.  

## Structure of Directories 

Below we show a sample walk-through with a binary tree-like structure. By default (only for demo), directories are geographically distributed and connected with each other as this topology. The name convention uses letter 'a' or 'b' to denote the left and right children in a tree. For example, level4aab is connected to its parent directory level3aa and its children directories level5aaba and level5aabb.

```
level1 (root)
level2a level2b
level3aa level3ab level3ba level3bb
level4aaa level4aab level4aba level4abb level4baa level4bab level4bba level4bbb  
level5aaaa level5aaab ...
level6aaaaa level6aaaab ...
```

By default, all the directoires run on localhost. The tree-like structure starts from port 5001, with the name of level1 (also called master directory or root directory). The single directory module named SingleDirectory runs on port 4999.

MongoDB runs on its default port 27017. To run MongoDB on another port: add `--port [port]` when starting the database, and change the configure files to direct apps to database. 

To release the ports occupied by directories when you got an error message saying ports are being used: `sudo kill -9 $(lsof -i:5001 -i:5002 -i:5003 -i:5004 -i:5005 -i:5006 -i:5007 -i:5008 -t)`.


## Access Control
So far, we have been able to set up a set of directories (as web applications). Now, let's review and configure the demos of access control features supported by DBAC. 

### Federated Identity Management 

We use [Authlib](https://authlib.org/) to implement a federated identtiy assertion model among directories based on OpenID. In a nutshell, one directory can rely on its counterparts to authenticate a user after some configurations. From a user's perspective, one can sign in a directory with the identity from another directory. 

#### Example 
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

> Now you can login level3aa with your username and password registered in level2b.


## Access Control Functionalities
The attribute-based policies generally specify in what conditions a thing can be accessed. Access rules are specified as policies, and requests are automatically generated when users request through the provided interfaces. Details about policy formats are based on the py_abac library. By default, requests are denied if there are no policies associated. When there is a conflict, the policy with highest priority dominates. 


### Distributed Attribute Retrieval 
The key vision behind the system is to retrieve attribute information from various resource providers. The authorization process is triggered by the "Authorize" button under "Attributes". The system identities and classifies the attributes required by the associated policies in the IoT directory. The user will be redirected to the user consent page, where they can choose from the set of possibly needed attributes what they allow the ABAC system to retrieve. The authorization and data retrieval process can be done iteratively until the system obtain enough attributes for the access decision.

Currently, the system assumes the sources of attributes: subject (user) attributes either stored in the identity server of the directory or from an OIDC provider (i.e., the identity server of a different directory), object attributes in TDs, and environmental attributes from third-party servers. Sample ABAC policies are in `/sample_data/attribute_policies` as JSON files.

### Third-Party Attribute Provider
"Third-party" simulates any external resource provider, which conveys a vision that some attributes are managed and provided by other servers. The implementation is again based on [Authlib](https://authlib.org/). For demo use, it contains any hypothetical information through third-parties (e.g., weather information including temperature and rainfall), and the underline technology is based on OAuth2. The configuration for the OAuth client is stored in "Droit/auth/providers_config.py". Run the sample server by `python app.py` in the "third-party" folder. To test the policy which requires attributes from third parties, you should ensure that the current user (e.g., "test_user") has such attributes in the database (manually insert some to the database before access).  

The sample server runs on port 5100, and for example, we need to manually input the values (username, weather, rainfall) to the third-party database for testing purpose. In addition, we need some sort of manually inputs:
``` 
redirect uri: `http://localhost:5004/auth/info_authorize`. 
allowed scope: `weather`. 
allowed grant type: `authorization_code`. 
allowed response type: `code`. 
```
After generating the client, put the client info to the "Droit/auth/providers_config.py". Indeed, this configuration is extremely similar to the federated identity management configuration (because OIDC is built upon OAuth). More on OAuth and OIDC implementation please refer to [Authlib](https://authlib.org/). 


### Additional Supported Features
To test the following features, please refer to the [`/sample_data/README.md`](https://github.com/Halleloya/DBAC/blob/master/sample_data/README.md).

1) Authorization based on geographic polygon: if someone's geo-coordinates is inside a geo-polygon, then access. 
2) Authorization based on dynamic attributes: we only implement access frequency (e.g., allow no more than 3 times per minutes) as one of the dynamic attributes at the current stage. 
3) Aggregate query across multiple directories. 

## Acknowledgement
We would like to thank Yifan, Hongfei, Ryan, and Andrea for their valuable inputs and contributions on the implementation of this prototype. 
