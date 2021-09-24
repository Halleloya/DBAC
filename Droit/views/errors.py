"""
Define the error pages for the project
"""

from flask import render_template

def register_error_page(app):
    @app.errorhandler(404)
    def page_not_found(e):
        # note that we set the 404 status explicitly
        return render_template('/errors/404.html', description = e), 404


    @app.errorhandler(401)
    def unauthorized (e):
        return render_template('/errors/401.html', description = e), 401
