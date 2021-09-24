from flask import Flask
from flask_mongoengine import MongoEngine
from .auth.models import auth_db
from .databases import init_dir_to_url, init_target_to_child_name, clear_database
from .databases import mongo
from .auth.oauth2 import oauth, config_oauth, initiate_providers
from .views.home import home
from .views.api import api
from .views.dashboard import dashboard
from .views.errors import register_error_page
from .auth import login_manager
from .auth.routes import auth
import os

SingleConfig = {
    'SECRET_KEY': os.urandom(128),
    'HOST_NAME': "SingleDirectory",
    'ENV_NAME': "SingleDirectory-Dev",
    'PORT': 4999,
    # mongo engine
    'MONGODB_HOST': 'localhost',
    'MONGODB_PORT': 27017,
    'MONGODB_DB': 'SingleDirectory',
    # pymongo
    'MONGO_URI': "mongodb://localhost:27017/SingleDirectory",
    # OAUth2
    'OAUTH2_JWT_ENABLED': True,
    'OAUTH2_JWT_ISS': 'http://localhost:4999/',
    'OAUTH2_JWT_KEY': 'SingleDirectory-secret',
    'OAUTH2_JWT_ALG': 'HS256',
    'OAUTH2_JWT_EXP': 3600
}

def main(init_db=True, debug=True, host='localhost'):
    app = Flask(__name__)

    # load flask-login
    login_manager.init_app(app)

    # load views(routers)
    app.register_blueprint(home, url_prefix = '/')
    app.register_blueprint(api, url_prefix = '/api')
    app.register_blueprint(dashboard, url_prefix='/dashboard')
    app.register_blueprint(auth, url_prefix='/auth')
    register_error_page(app)

    # initialize Flask app
    app.config.update(**SingleConfig)

    # initialize db connections for mongo engine, and pymongo
    mongo_db = MongoEngine(app)
    mongo.init_app(app)
    # initialize flask-sqlalchemy used by OAuth 2.0 and OpenID Connect 1.0
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./SingleDirectory.db'
    auth_db.init_app(app)
    # initialize OAuth2.0 configuration
    oauth.init_app(app)
    config_oauth(app)
    initiate_providers('SingleDirectory')
    
    if init_db:
        with app.app_context():
            # Create all tables for authentication
            auth_db.create_all()
        # Initialize IoT related tables in MongoDB
        clear_database()
        init_dir_to_url('SingleDirectory')
        init_target_to_child_name('SingleDirectory')
    app.run(debug = debug, host= host, port= app.config["PORT"])
    
if __name__ == "__main__":
    main()