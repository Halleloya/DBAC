"""
The classses defined in this file is comprehensively used in OpenID Connect work flow.
While the User class is also served as the ORM class in the local user management, all other
classes (except the UserAccountTypeEnum) is required by the Authlib library to represent some object.
"""
import enum
import json
from flask_sqlalchemy import SQLAlchemy
from flask import current_app as app

from flask_login import UserMixin
from werkzeug.security import gen_salt
from authlib.oidc.core import UserInfo
from authlib.integrations.sqla_oauth2 import (
    OAuth2ClientMixin,
    OAuth2TokenMixin,
    OAuth2AuthorizationCodeMixin
)
from authlib.oidc.core.grants import (
    OpenIDCode as _OpenIDCode
)
from authlib.oauth2.rfc6749.grants import (
    AuthorizationCodeGrant as _AuthorizationCodeGrant,
)

auth_db = SQLAlchemy()

"""
Lists of attributes that can be accessed from user provider or external oauth2 server
"""
auth_user_attr_default = {"address": None, "phone_number": None}
auth_server_attr_default = {"temperature": None, "rainfall": None, "polygon": None}


class UserAccountTypeEnum(enum.Enum):
    """Enumeration class to represent the user's information

    When the user is registered locally, the value should be 'local'
    When the user is logged in via OpenID Connect, the value should be 'oidc'
    """
    local = 0
    oidc = 1

class Policy(auth_db.Model):
    __tablename__ = 'Policy'
    policy_id = auth_db.Column(auth_db.Integer, nullable = False , primary_key = True)
    uid = auth_db.Column(auth_db.String(36), nullable = False)
    location = auth_db.Column(auth_db.String(128),nullable=False)
    policy_json = auth_db.Column(auth_db.Text, nullable = False)
    user_id = auth_db.Column(auth_db.Integer, auth_db.ForeignKey('user.id'),
        nullable=False)
    
    def get_policy_id(self):
        return self.policy_id
    def get_uid(self):
        return self.uid
    def get_policy_json(self):
        return self.policy_json
    def get_location(self):
        return self.location
    def get_user_id(self):
        return self.user_id


class AuthAttribute(auth_db.Model):
    """
    A temporary storage database for holding attributes accessed via authorization
    """
    __tablename__ = 'auth_attribute'

    id = auth_db.Column(auth_db.Integer, primary_key=True)
    user_id = auth_db.Column(auth_db.Integer, auth_db.ForeignKey('user.id', ondelete='CASCADE'))
    user = auth_db.relationship('User')
    user_attributes = auth_db.Column(auth_db.Text, default=json.dumps(auth_user_attr_default))
    server_attributes = auth_db.Column(auth_db.Text, default=json.dumps(auth_server_attr_default))

    def get_user_attributes(self):
        user_attr_dict = json.loads(self.user_attributes)
        return user_attr_dict

    def get_server_attributes(self):
        server_attr_dict = json.loads(self.server_attributes)
        return server_attr_dict

    def set_user_attributes(self, user_attr_dict):
        user_attr = json.dumps(user_attr_dict)
        self.user_attributes = user_attr
        auth_db.session.commit()

    def set_server_attributes(self, server_attr_dict):
        server_attr = json.dumps(server_attr_dict)
        self.server_attributes = server_attr
        auth_db.session.commit()


class User(auth_db.Model, UserMixin):
    """ORM class that represents the user table

    The user class is used for local user management (register, login) and also
    openid user login
    """

    # specify the corresponding table name
    __tablename__ = 'user'

    id = auth_db.Column(auth_db.Integer, primary_key=True)
    username = auth_db.Column(auth_db.String(30), nullable=False)
    email = auth_db.Column(auth_db.String(35), unique=True, nullable=False)
    address = auth_db.Column(auth_db.String(128), nullable=True)
    phone_number = auth_db.Column(auth_db.String(32), nullable=True)
    # if the user is loggedin using oidc, the password is random assigned
    password = auth_db.Column(auth_db.Text, nullable=False)
    account_type = auth_db.Column(auth_db.Enum(UserAccountTypeEnum))
    provider_name = auth_db.Column(auth_db.String(80))
    policy = auth_db.relationship('Policy', backref='user', lazy=True)

    def __str__(self):
        return f"Name: {self.username}, Email:{self.email}"

    def get_user_id(self):
        """A user identification method required by authlib

        the user's unique identifier must be returned, in order to check the identity
        """
        return self.id

    def get_email(self):
        return self.email

    def get_username(self):
        return self.username
        
    def get_id(self):
        """A user identification method required by flask-login

        the user's unique identifier must be returned in unicode format, in order to
        identify the user
        """
        return int_to_unicode(self.id)

    def get_provider_name(self):
        return self.provider_name

    def get_email(self):
        return self.email

    def get_address(self):
        return self.address

    def get_phone(self):
        return self.phone_number

    def set_address(self, address):
        self.address = address
        auth_db.session.commit()

    def get_policy(self):
        return self.policy

class OAuth2Client(auth_db.Model, OAuth2ClientMixin):
    """OAuth2/OpenID Connect client application class

    The client class is manipulated by authlib library, each object represents
    a single OAuth2 client application. It is also a ORM class that mapping the
    table in database to a python object
    """

    __tablename__ = 'oauth2_client'

    id = auth_db.Column(auth_db.Integer, primary_key=True)
    # scope = auth_db.Column(auth_db.String(length=40))
    scope = auth_db.Column(auth_db.Text, default='')
    # user_id = db.Column(
    #     db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    # user = db.relationship('User')


class OAuth2AuthorizationCode(auth_db.Model, OAuth2AuthorizationCodeMixin):
    """OAuth2 Authorization code class

    This is a ORM class that represents a single authorization code
    The code is initially returned by the provider after successful consent
    """

    __tablename__ = 'oauth2_code'

    id = auth_db.Column(auth_db.Integer, primary_key=True)
    user_id = auth_db.Column(
        auth_db.Integer, auth_db.ForeignKey('user.id', ondelete='CASCADE'))
    user = auth_db.relationship('User')


class OAuth2Token(auth_db.Model, OAuth2TokenMixin):
    """Representing the real token (Access Token, Refresh Token) in OAuth2 flow

    This is a ORM class that is used as the token object
    """
    __tablename__ = 'oauth2_token'

    id = auth_db.Column(auth_db.Integer, primary_key=True)
    name = auth_db.Column(auth_db.String(length=40))
    token_type = auth_db.Column(auth_db.String(length=40))
    access_token = auth_db.Column(auth_db.String(length=200))
    refresh_token = auth_db.Column(auth_db.String(length=200))
    id_token = auth_db.Column(auth_db.String(length=200))
    expires_at = auth_db.Column(auth_db.Integer)
    expires_in = auth_db.Column(auth_db.Integer)
    # scope = auth_db.Column(auth_db.String(length=40))
    user_id = auth_db.Column(
        auth_db.Integer, auth_db.ForeignKey('user.id', ondelete='CASCADE'))
    user = auth_db.relationship('User')

    def to_token(self):
        return dict(
            access_token=self.access_token,
            token_type=self.token_type,
            refresh_token=self.refresh_token,
            id_token=self.id_token,
            expires_at=self.expires_at,
            expires_in=self.expires_in,
            scope=self.scope,
            name=self.name
        )


class AuthorizationCodeGrant(_AuthorizationCodeGrant):
    """Representation of OAuth2 Authorization Code Grant Type

    The configuration of OAuth2 providers requires the allowed code flow to be specified.
    The Authorization code flow is the norm for using OAuth2.0, and this class is the config
    class for such flow.
    """

    def create_authorization_code(self, client, grant_user, request):
        code = gen_salt(48)
        # nonce = request.data.get('nonce')
        item = OAuth2AuthorizationCode(
            code=code,
            client_id=client.client_id,
            redirect_uri=request.redirect_uri,
            scope=request.scope,
            user_id=grant_user.id,
            # nonce=nonce,
        )
        auth_db.session.add(item)
        auth_db.session.commit()
        return code

    def parse_authorization_code(self, code, client):
        item = OAuth2AuthorizationCode.query.filter_by(
            code=code, client_id=client.client_id).first()
        if item and not item.is_expired():
            return item

    def delete_authorization_code(self, authorization_code):
        auth_db.session.delete(authorization_code)
        auth_db.session.commit()

    def authenticate_user(self, authorization_code):
        return User.query.get(authorization_code.user_id)


class OpenIDCode(_OpenIDCode):
    """A ORM class that represents the ID token in the OpenID Connect process

    The class is different from the OAuth2Token, while the later one represents
    a general token(Access token, refresh token) used in most OAuth2.0 work flow
    """

    def exists_nonce(self, nonce, request):
        """Check whether the nonce is is already used

        For this implementation, the validation of nonce is ignored,
        so this method always returns False

        Usually the nonce examination should be done in the database, using the client's
        id and the nonce parameter as the filter condition. Such as the following code
            exists = OAuth2AuthorizationCode.query.filter_by(
                client_id=request.client_id, nonce=nonce
            ).first()
            return bool(exists)
        """
        return False

    def get_jwt_config(self, grant):
        """Return the configuration of the JWT token header

        """
        app_jwt_config = {
            'key': app.config["OAUTH2_JWT_KEY"],
            'alg': app.config["OAUTH2_JWT_ALG"],
            'iss': app.config["OAUTH2_JWT_ISS"],
            'exp': app.config["OAUTH2_JWT_EXP"],
        }
        return app_jwt_config

    def generate_user_info(self, user, scope):
        """Generate the user information that will be used to encode the ID token

        A 'UserInfo' object must be returned to specify the related user's information
        The class is provided by authlib library, and only the following properties
        are allowed to provide user's information.

        [
             'sub', 'name', 'given_name', 'family_name', 'middle_name', 'nickname',
             'preferred_username', 'profile', 'picture', 'website', 'email',
             'email_verified', 'gender', 'birthdate', 'zoneinfo', 'locale',
             'phone_number', 'phone_number_verified', 'address', 'updated_at',
        ]
        For more details, please refer to authlib documentation or UserInfo's definition
        """
        user_info = UserInfo(sub=str(user.id), username=user.username, email=user.email)
        if 'address' in scope:
            user_info['address'] = user.get_address()
        if 'phone_number' in scope:
            user_info['phone_number'] = user.get_phone()

        return user_info


def int_to_unicode(number):
    """Convert the integer 'number' to 'unicode' str

    """
    return chr(number)


def unicode_to_int(unicode_str):
    """Convert the unicode 'unicode_str' to corresponding integer

    """
    return ord(unicode_str)
