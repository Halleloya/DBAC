from flask_login import LoginManager
from .models import User, unicode_to_int, AuthAttribute

# Used by flask_login to maintain the current user state
login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    """Used by flask-login library to retrieve user's identification using its id

    """
    return User.query.filter_by(id=unicode_to_int(user_id)).first()
