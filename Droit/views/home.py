from flask import Blueprint, render_template, request, session, redirect, url_for
from flask_login import current_user
from ..utils import get_auth_attributes
home = Blueprint('home', __name__)


@home.route('/')
@home.route('/index')
@home.route('/home')
def index():
    """Render the home page for the project

    Returns:
        response: the flask response object representing the HTML page
    """
    return render_template("home/index.html")


@home.route('/about', methods=['GET', 'POST'])
def about():
    """Render the abount page for the project

    Returns:
        response: the flask response object representing the HTML page
    """
    if current_user.is_anonymous:
        # redirect to login page if not logged in
        return redirect(url_for('auth.login'))
    username = current_user.get_username()
    email = current_user.get_email()
    address = current_user.get_address()
    auth_attributes = get_auth_attributes()
    auth_user_attributes = auth_attributes[0]
    if not address:
        address = auth_user_attributes.get('address', None)
    phone_number = current_user.get_phone()
    if not phone_number:
        phone_number = auth_user_attributes.get('phone_number', None)

    policies = []
    for p in current_user.get_policy():
        cur = {'uid': p.get_uid(), 'location': p.get_location(), 'policy_json': p.get_policy_json()}
        policies.append(cur)
    print(policies)
    print(current_user.get_policy())
    return render_template("home/about.html",
                           username=username, email=email, address=address, phone_number=phone_number, policies=policies)


@home.route('/contact')
def contact():
    """Render the contact page for the project

    Returns:
        response: the flask response object representing the HTML page
    """
    return render_template("home/contact.html")


@home.route('/delete_policy')
def policy_decision():

    return render_template('home/about.html', tagname = 'delete_policy')