"""
Insta485 index (main) view.

URLs include:
/
"""
import flask
import insta485

import uuid
import hashlib
import pathlib



@insta485.app.route('/users/<user_url_slug>/')
def show_user(user_url_slug):
    if 'username' in flask.session:
        loggedIn = flask.session['username']
        # Connect to database
        connection = insta485.model.get_db()
        
        context = {"username":user_url_slug,
                    "logname": loggedIn
                    }                    
        return flask.render_template("user.html", **context)
    else:
        return flask.render_template("login.html")        

