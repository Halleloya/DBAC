import click
import subprocess
from flask_mongoengine import MongoEngine
from Droit import create_app
from Droit.auth.models import auth_db
from Droit.databases import init_dir_to_url, init_target_to_child_name, clear_database
from Droit.databases import mongo
from Droit.auth.oauth2 import oauth, config_oauth, initiate_providers
from config import dev_config
from Droit.utils import register_new_schema
from Droit.views import GeographyHelper


@click.command()
@click.option('--init-db', default=True, type=bool, help="Clean previous data and insert URL mappings into database.\nBy default it's True")
@click.option('--debug', default=True, type=bool, help="Use Debug Mode.\nBy default it's True.")
@click.option('--host', default='localhost', type=str, help="The host that this app is running on.\n By default it is localhost")
@click.option('--level', default='level1', type=click.Choice(['level1','level2a','level2b','level3aa','level3ab','level4aba','level4abb','level5abba','level5abbb'], case_sensitive=False), 
                    help = "Specify which directory to run.\nBy default its the level1.\n If the mode is 'all', this argument will be ignored.")
def main(level, init_db, debug, host):
    """
    Load all configurations for the application, and then start running
    """

    app = create_app()
    # initialize Flask app
    app_config = dev_config[level]
    app.config.update(**app_config.to_dict())

    # initialize db connections for mongo engine, and pymongo
    mongo_db = MongoEngine(app)
    mongo.init_app(app)
    # initialize flask-sqlalchemy used by OAuth 2.0 and OpenID Connect 1.0
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///./{level}.db'
    auth_db.init_app(app)
    # initialize OAuth2.0 configuration
    oauth.init_app(app)
    config_oauth(app)
    initiate_providers(level)
    register_new_schema()
    
    if init_db:
        with app.app_context():
            # Create all tables for authentication
            auth_db.create_all()
        # Initialize IoT related tables in MongoDB
        clear_database()
        init_dir_to_url(level)
        init_target_to_child_name(level)
    GeographyHelper.AddLevelBoundingBox(level, dev_config[level].BOUNDING_BOX_COORDS)
    app.run(debug = debug, host=host, port= app.config["PORT"])

if __name__ == "__main__":
    main()