from flask import Flask

#import config
from .views.home import home
from .views.api import api
from .views.dashboard import dashboard
from .views.errors import register_error_page
from .auth import login_manager
from .auth.routes import auth

def create_app() -> Flask:
    """an flask app instance and initialize basic modules and plugins
    
    Returns:
        app: the initialized flask app instance
    """
    app = Flask(__name__)
    #app.config.from_object(config.DevConfig)

    # load flask-login
    login_manager.init_app(app)

    # load views(routers)
    app.register_blueprint(home, url_prefix = '/')
    app.register_blueprint(api, url_prefix = '/api')
    app.register_blueprint(dashboard, url_prefix='/dashboard')
    app.register_blueprint(auth, url_prefix='/auth')
    register_error_page(app)
    return app
