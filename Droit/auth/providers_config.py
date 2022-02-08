"""
Preconfig the providers information for each directory

The first level key name is the client's name.
For each client, the second level key-value pair specifies its client information in the corresponding provider

For example, 'providers_config.level1.level2' records the client information of level1 with level2 as the provider

'client_id/client_secret':  the client's registered information for the specified provider. Both of them must match the
    data registered in the provider's database in order to perform any oauth functions
'access_token_url': API endpoint for retrieving access token and id token
'authorize_url':    API endpoint for user authentication and authorization code retrieve
'api_base_url':     Base API endpoint of the provider

In this project, the OpenID Connect Providers are predefined in this file, and will be loaded
when application starts. Alternatively, providers can be registerd using 'oauth.register' method
afterward and persistent into databases for long-term reuse.
"""

providers_config = {
    # providers for level1 directory.
    "level1": {
        "level2a": {
            "client_id": 'm8d8ZjrMRQNuupmNsJT5m0qT',
            "client_secret": 'kRDS2qX47fcA3Oc9DPOvWg7TrUMFYPJDw5LYO7obVegYbMLN',
            "access_token_url": 'http://localhost:5002/auth/oidc_token',
            "access_token_params": None,
            "authorize_url": 'http://localhost:5002/auth/oidc_authorize',
            "authorize_params": None,
            "api_base_url": 'http://localhost:5002/api',
            "client_kwargs": {
                'scope': 'openid profile',
                'token_endpoint_auth_method': 'client_secret_basic'}
        },
        "level2b": {

        },
        "level3": {

        },
        "level4a": {

        },
        "level4b": {

        },
        "level5a": {

        },
        "level5b": {

        }
    },
    # providers for level3aa directory
    "level3aa": {
        "level2b": {
            "client_id": 'MeQnvnCScziNu75YdKaPDexe',
            "client_secret": 'Xi38hWVQWdmLIqiDnUScm0X10NjXt6XrKWnZLgHNBrU4unNb',
            "access_token_url": 'http://localhost:5003/auth/oidc_token',
            "access_token_params": None,
            "authorize_url": 'http://localhost:5003/auth/oidc_authorize',
            "authorize_params": None,
            "api_base_url": 'http://localhost:5003/api',
            "client_kwargs": {
                'scope': 'openid profile address phone_number',
                'token_endpoint_auth_method': 'client_secret_basic'}
        }
    }
}

oauth2_server_config = {
    "server_url": "http://127.0.0.1:5100",
    "client_id": "1WCyaYBeXRKDM4Vvf1nUseJm",
    "client_secret": "dyaIWavG7IdgkrdkiX8BwNKvRaxMru6NjnQcAn8Wb5JOFA4z",
    "grant_type": "authorization_code",
    "response_type": "code",
    "scope": "weather",
    "code": None,
    "access_token": None,
    "access_scope": []
}
