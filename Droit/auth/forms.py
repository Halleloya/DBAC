"""
Classes defined in this filed is used by WTForms library to assist HTML form
rendering and validation.

"""

from wtforms import Form, StringField, validators, SelectField


class OAuthClientRegisterForm(Form):
    """Form class for OIDC client registration.

    The field contained in this class will be used to render the client registration
    form's input fields and do the validation after the form is submitted.
    """
    client_name = StringField('Client Name', [validators.InputRequired('Please enter a Client Name'),
                                              validators.Length(min=4, max=35)])
    client_uri = StringField('Client URI', [validators.URL(require_tld=False, message="Please enter a valid URI"),
                                            validators.Length(min=6, max=200)])
    redirect_uri = StringField("Redirect URI", [validators.URL(require_tld=False, message="Please enter a valid URI"),
                                                validators.Length(min=6, max=200)])
    scope = SelectField("Allowed Scopes", choices=[('openid profile', 'openid profile'), ('openid profile address phone_number', 'openid profile address phone_number'), ('openid profile address', 'openid profile address')])
    grant_type = SelectField("Allowed Grant Types", choices=[('authorization_code', 'authorization_code')])
    response_type = SelectField("Allowed Response Types", choices=[('code', 'code')])
    token_endpoint_auth_method = SelectField("Token Endpoint Auth Method",
                                             choices=[('client_secret_basic', 'client_secret_basic'), ('none', 'none')])
