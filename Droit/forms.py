"""
Classes defined in this file is used together with HTML template to validiate and render form fields using WTF python library
HTML forms are encouraged to use this library to help with data validation, CSRF protection and fields rendering

Basically, each class defined in this file has properties that works with the HTML form fields rendering and validation.

For more information, Please refer to its website: https://wtforms.readthedocs.io/en/2.3.x/
"""

from .models import ThingDescription
from flask_mongoengine.wtf import model_form
from wtforms import Form, BooleanField, StringField, validators, PasswordField

ThingDescriptionForm = model_form(ThingDescription)

class UserForm(Form):
    """
    Basic user form class. It defines fields that are shared among other user management forms
    This class shoulbe an abstract class template that should not initialize any objects
    """
    email = StringField('Email Address', [validators.InputRequired(), validators.Length(min=6, max=35), 
                    validators.Email('Please enter a valid email address')])
    address = StringField('Address', [validators.Optional(), validators.Length(min=0, max=128)])
    phone_number = StringField('Phone Number', [validators.Optional(), validators.Length(min=0, max=32)])
    password = PasswordField('Password', [validators.InputRequired(),validators.Length(min=6, max=50)])

class UserLoginForm(UserForm):
    """
    WTForms class for "User Login", used by Jinja2 template to generate corresponding Input fields
    """
    remember_me = BooleanField('Remember Me')
    
class UserRegisterForm(UserForm):
    """
    WTForms class for "User Register", used by Jinja2 template to generate corresponding Input fields
    """
    
    username = StringField('Username', [validators.InputRequired(),validators.Length(min=4, max=30)])
    retype_password = PasswordField('Confirm Password', [validators.EqualTo('password', 'Passwords must match')])

class QueryForm(Form):
    """
    WTForms class for "Search" dashboard endpoint. 
    It contains the search fields in the query form.
    """
    location = StringField("Location")
    thing_type = StringField("Thing Type")
    thing_id = StringField("Thing ID")

class DeleteForm(Form):
    """
    WTForms class for "Delete" dashboard endpoint. 
    """
    location = StringField("Location")
    thing_id = StringField("Thing ID")

class RelocateForm(Form):
    """
    WTForms class for "Relocate" dashboard endpoint. 
    """
    from_location = StringField("From")
    to_location = StringField("To")
    thing_id = StringField("Thing ID")
