import os

"""
Set up the configuration for flask environment using classes

:BaseConfig: the parent class for all configuration class, used for common settings

:TestConfig: the configuration class for test environment
:DevConfig: the configuration class for development environment
:DepConfig: the configuration class for deployment environment
"""


class BaseConfig(object):
    # Used for flask session to generate session id
    SECRET_KEY = os.urandom(128)

    @classmethod
    def to_dict(cls):
        """
        Convert attributes to a dictionary form, which is used for Eve library setting
        """
        return {attr: getattr(cls, attr) for attr in dir(cls) if attr.isupper()}


class TestConfig(BaseConfig):
    # Testing Environment Configuration
    ENV_NAME = "Test"


"""
Development configurations
"""
class DevConfig(BaseConfig):
    # Development Environment Configuration
    ENV_NAME = "Development"
    # Mongo Engine
    MONGODB_HOST = os.getenv('MONGODB_HOST', 'localhost')
    MONGODB_PORT = 27017
    BOUNDING_BOX_COORDS = []
    level1_host = 'http://localhost:5001/'
    level2a_host = 'http://localhost:5002/'
    level2b_host = 'http://localhost:5003/'
    level3aa_host = 'http://localhost:5004/'
    level3ab_host = 'http://localhost:5005/'
    level4aba_host = 'http://localhost:5006/'
    level4abb_host = 'http://localhost:5007/'
    level5abba_host = 'http://localhost:5008/'
    level5abbb_host = 'http://localhost:5009/'

    if os.getenv('CDN_DOMAIN'):
        level1_host = 'http://droit-master-service:5001/'
        level2a_host = 'http://droit-level2a-service:5002/'
        level2b_host = 'http://droit-level2b-service:5003/'
        level3aa_host = 'http://droit-level3aa-service:5004/'
        level3ab_host = 'http://droit-level3ab-service:5005/'
        level4aba_host = 'http://droit-level4aba-service:5006/'
        level4abb_host = 'http://droit-level4abb-service:5007/'
        level5abba_host ='http://droit-level5abba-service:5008/'
        level5abbb_host = 'http://droit-level5abbb-service:5009/'


class Level1DevConfig(DevConfig):
    BOUNDING_BOX_COORDS =   [
                                [
                                    -73.9413571357727,
                                    40.847376876001356
                                ],
                                [
                                    -73.94136786460875,
                                    40.84621629553305
                                ],
                                [
                                    -73.93925428390502,
                                    40.846524703514575
                                ],
                                [
                                    -73.93953323364258,
                                    40.84750672989431
                                ],
                                [
                                    -73.9413571357727,
                                    40.847376876001356
                                ]
                            ]
    HOST_NAME = "level1"
    ENV_NAME = "Level1-Dev"
    PORT=5001
    # mongo engine
    MONGODB_PORT = 27017
    MONGODB_DB = 'level1'
    # pymongo
    MONGO_URI = "mongodb://" + DevConfig.MONGODB_HOST + ":27017/level1"
    # OAUth2
    OAUTH2_JWT_ENABLED = True
    OAUTH2_JWT_ISS = DevConfig.level1_host
    OAUTH2_JWT_KEY = 'level1-secret'
    OAUTH2_JWT_ALG = 'HS256'
    OAUTH2_JWT_EXP = 3600

class Level2aDevConfig(DevConfig):
    BOUNDING_BOX_COORDS =   [
                                [
                                    -73.94280552864075,
                                    40.845696868319834
                                ],
                                [
                                    -73.94293427467346,
                                    40.84398435288899
                                ],
                                [
                                    -73.93996238708496,
                                    40.844487561066394
                                ],
                                [
                                    -73.94132494926453,
                                    40.84564817180984
                                ],
                                [
                                    -73.94280552864075,
                                    40.845696868319834
                                ]
                            ]
    HOST_NAME = "level2a"
    ENV_NAME = "Level2a-Dev"
    PORT=5002
    MONGODB_PORT = 27017
    MONGODB_DB = 'level2a'
    MONGO_DBNAME = 'level2a'
    MONGO_URI = "mongodb://" + DevConfig.MONGODB_HOST + ":27017/level2a"
    # OAUth2
    OAUTH2_JWT_ENABLED = True
    OAUTH2_JWT_ISS = DevConfig.level2a_host
    OAUTH2_JWT_KEY = 'level2a-secret'
    OAUTH2_JWT_ALG = 'HS256'
    OAUTH2_JWT_EXP = 3600


class Level2bDevConfig(DevConfig):
    BOUNDING_BOX_COORDS =   [
                                [
                                    -73.939071893692,
                                    40.84584295763504
                                ],
                                [
                                    -73.93896460533142,
                                    40.84451190975225
                                ],
                                [
                                    -73.93751621246338,
                                    40.84522613389123
                                ],
                                [
                                    -73.93802046775818,
                                    40.84593223428027
                                ],
                                [
                                    -73.939071893692,
                                    40.84584295763504
                                ]
                            ]
    HOST_NAME = "level2b"
    ENV_NAME = "Level2b-Dev"
    PORT=5003
    MONGODB_PORT = 27017
    MONGODB_DB = 'level2b'
    MONGO_DBNAME = 'level2b'
    MONGO_URI = "mongodb://" + DevConfig.MONGODB_HOST + ":27017/level2b"
    # OAUth2
    OAUTH2_JWT_ENABLED = True
    OAUTH2_JWT_ISS = DevConfig.level2b_host
    OAUTH2_JWT_KEY = 'level2b-secret'
    OAUTH2_JWT_ALG = 'HS256'
    OAUTH2_JWT_EXP = 3600

class Level3aaDevConfig(DevConfig):
    BOUNDING_BOX_COORDS =   [
                                [
                                    -73.94275188446045,
                                    40.843164602353745
                                ],
                                [
                                    -73.94260168075562,
                                    40.842182511630114
                                ],
                                [
                                    -73.94056320190428,
                                    40.842190628142006
                                ],
                                [
                                    -73.94086360931396,
                                    40.84348114089084
                                ],
                                [
                                    -73.94275188446045,
                                    40.843164602353745
                                ]
                            ]
    HOST_NAME = "level3aa"
    ENV_NAME = "Level3aa-Dev"
    PORT=5004
    MONGODB_PORT = 27017
    MONGODB_DB = 'level3aa'
    MONGO_DBNAME = 'level3aa'
    MONGO_URI = "mongodb://" + DevConfig.MONGODB_HOST + ":27017/level3aa"
    # OAUth2
    OAUTH2_JWT_ENABLED = True
    OAUTH2_JWT_ISS = DevConfig.level3aa_host
    OAUTH2_JWT_KEY = 'level3aa-secret'
    OAUTH2_JWT_ALG = 'HS256'
    OAUTH2_JWT_EXP = 3600

class Level3abDevConfig(DevConfig):
    BOUNDING_BOX_COORDS =   [
                                [
                                    -73.93881440162659,
                                    40.84370839839537
                                ],
                                [
                                    -73.93870711326599,
                                    40.84227990970727
                                ],
                                [
                                    -73.93702268600464,
                                    40.84310778758449
                                ],
                                [
                                    -73.93735527992249,
                                    40.844081748318295
                                ],
                                [
                                    -73.93881440162659,
                                    40.84370839839537
                                ]
                            ]
    HOST_NAME = "level3ab"
    ENV_NAME = "Level3ab-Dev"
    PORT=5005
    MONGODB_PORT = 27017
    MONGODB_DB = 'level3ab'
    MONGO_DBNAME = 'level3ab'
    MONGO_URI = "mongodb://" + DevConfig.MONGODB_HOST + ":27017/level3ab"
    # OAUth2
    OAUTH2_JWT_ENABLED = True
    OAUTH2_JWT_ISS = DevConfig.level3ab_host
    OAUTH2_JWT_KEY = 'level3ab-secret'
    OAUTH2_JWT_ALG = 'HS256'
    OAUTH2_JWT_EXP = 3600

class Level4abaDevConfig(DevConfig):
    BOUNDING_BOX_COORDS =   [
                                [
                                    -73.94261240959167,
                                    40.8414601380904
                                ],
                                [
                                    -73.94240856170654,
                                    40.840429321766024
                                ],
                                [
                                    -73.94038081169127,
                                    40.84051048898719
                                ],
                                [
                                    -73.9408528804779,
                                    40.841565653817554
                                ],
                                [
                                    -73.94261240959167,
                                    40.8414601380904
                                ]
                            ]
    HOST_NAME = "level4aba"
    ENV_NAME = "Level4aba-Dev"
    PORT=5006
    MONGODB_PORT = 27017
    MONGODB_DB = 'level4aba'
    MONGO_DBNAME = 'level4aba'
    MONGO_URI = "mongodb://" + DevConfig.MONGODB_HOST + ":27017/level4aba"
    # OAUth2
    OAUTH2_JWT_ENABLED = True
    OAUTH2_JWT_ISS = DevConfig.level4aba_host
    OAUTH2_JWT_KEY = 'level4aba-secret'
    OAUTH2_JWT_ALG = 'HS256'
    OAUTH2_JWT_EXP = 3600

class Level4abbDevConfig(DevConfig):
    BOUNDING_BOX_COORDS =   [
                                [
                                    -73.9384388923645,
                                    40.84173610194502
                                ],
                                [
                                    -73.93848180770874,
                                    40.84060788952139
                                ],
                                [
                                    -73.93709778785704,
                                    40.84089197359531
                                ],
                                [
                                    -73.93689393997192,
                                    40.841833500678185
                                ],
                                [
                                    -73.93745183944702,
                                    40.84225556020139
                                ],
                                [
                                    -73.9384388923645,
                                    40.84173610194502
                                ]
                            ]
    HOST_NAME = "level4abb"
    ENV_NAME = "Level4abb-Dev"
    PORT=5007
    MONGODB_PORT = 27017
    MONGODB_DB = 'level4abb'
    MONGO_DBNAME = 'level4abb'
    MONGO_URI = "mongodb://" + DevConfig.MONGODB_HOST + ":27017/level4abb"
    # OAUth2
    OAUTH2_JWT_ENABLED = True
    OAUTH2_JWT_ISS = DevConfig.level4abb_host
    OAUTH2_JWT_KEY = 'level4abb-secret'
    OAUTH2_JWT_ALG = 'HS256'
    OAUTH2_JWT_EXP = 3600


class Level5abbaDevConfig(DevConfig):
    BOUNDING_BOX_COORDS =   [
                                [
                                    -73.94221544265747,
                                    40.83976374680333
                                ],
                                [
                                    -73.94223690032959,
                                    40.83853809737505
                                ],
                                [
                                    -73.94014477729797,
                                    40.838716670225324
                                ],
                                [
                                    -73.94040226936339,
                                    40.83982868124022
                                ],
                                [
                                    -73.94221544265747,
                                    40.83976374680333
                                ]
                            ]
    HOST_NAME = "level5abba"
    ENV_NAME = "Level5abba-Dev"
    PORT=5008
    MONGODB_PORT = 27017
    MONGODB_DB = 'level5abba'
    MONGO_DBNAME = 'level5abba'
    MONGO_URI = "mongodb://" + DevConfig.MONGODB_HOST + ":27017/level5abba"
    # OAUth2
    OAUTH2_JWT_ENABLED = True
    OAUTH2_JWT_ISS = DevConfig.level5abba_host
    OAUTH2_JWT_KEY = 'level5abba-secret'
    OAUTH2_JWT_ALG = 'HS256'
    OAUTH2_JWT_EXP = 3600


class Level5abbbDevConfig(DevConfig):
    BOUNDING_BOX_COORDS =   [
                                [
                                    -73.93858909606932,
                                    40.84001536739199
                                ],
                                [
                                    -73.93858909606932,
                                    40.83874913796459
                                ],
                                [
                                    -73.93749475479126,
                                    40.83904134690241
                                ],
                                [
                                    -73.93752694129944,
                                    40.840137118946856
                                ],
                                [
                                    -73.93858909606932,
                                    40.84001536739199
                                ]
                            ]
    HOST_NAME = "level5abbb"
    ENV_NAME = "Level5abbb-Dev"
    PORT=5009
    MONGODB_PORT = 27017
    MONGODB_DB = 'level5abbb'
    MONGO_DBNAME = 'level5abbb'
    MONGO_URI = "mongodb://" + DevConfig.MONGODB_HOST + ":27017/level5abbb"
    # OAUth2
    OAUTH2_JWT_ENABLED = True
    OAUTH2_JWT_ISS = DevConfig.level4abb_host
    OAUTH2_JWT_KEY = 'level5abbb-secret'
    OAUTH2_JWT_ALG = 'HS256'
    OAUTH2_JWT_EXP = 3600


dev_config = {
    "level1": Level1DevConfig,
    "level2a": Level2aDevConfig,
    "level2b": Level2bDevConfig,
    "level3aa": Level3aaDevConfig,
    "level3ab": Level3abDevConfig,
    "level4aba": Level4abaDevConfig,
    "level4abb": Level4abbDevConfig,
    "level5abba": Level5abbaDevConfig,
    "level5abbb": Level5abbbDevConfig
}


class DepConfig(BaseConfig):
    # Deployment Environment Configurations
    ENV_NAME = "Deployment"
