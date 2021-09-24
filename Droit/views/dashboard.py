from flask import Blueprint, render_template
from ..forms import RelocateForm, DeleteForm, QueryForm
from ..models import DirectoryNameToURL

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/')
@dashboard.route('/home')
@dashboard.route('/directories')
def home():
    """
    Render the home page for the 'dashboard' module
    This returns the names and URLs of adjacent directories
    """
    return render_template("dashboard/directories.html", tagname = 'home', directories = DirectoryNameToURL.objects.all())


@dashboard.route('/query')
def query():
    """
    Render the thing description query page for the 'dashboard' module
    """
    return render_template("dashboard/query.html", tagname = 'query', form = QueryForm())

@dashboard.route('/delete')
def delete():
    """
    Render the thing description deletion page for the 'dashboard' module
    """
    return render_template("dashboard/delete.html", tagname = 'delete', form = DeleteForm())

@dashboard.route('/relocate')
def relocate():
    """
    Render the thing description relocation page for the 'dashboard' module
    """
    return render_template("dashboard/relocate.html", tagname = 'relocate', form = RelocateForm())

@dashboard.route('/script')
def script():
    """
    Render the thing description script query page for the 'dashboard' module
    """
    return render_template("dashboard/script.html", tagname = 'script')

@dashboard.route('/register')
def register():
    """
    Render the thing description register page for the 'dashboard' module
    """
    return render_template('dashboard/register.html', tagname = 'register')

@dashboard.route('/policy')
def policy():
    """
    Render the policy page for the 'dashboard' module
    """
    return render_template('dashboard/policy.html', tagname = 'policy')

@dashboard.route('/policy_decision')
def policy_decision():
    """
    Render the request page for the 'dashboard' module
    """
    return render_template('dashboard/policy_decision.html', tagname = 'policy_decision')
