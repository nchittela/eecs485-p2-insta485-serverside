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

@insta485.app.route('/likes/', methods=['POST'])
def do_likes():
    target = flask.request.args.get('target')
    operation = flask.request.form['operation']
    owner = flask.session['username']
    postid = flask.request.form['postid']

    # get login data from database
    # Connect to database
    connection = insta485.model.get_db()

    if operation == 'like':
        # Query database for user's hashed password
        cur = connection.execute(
            "INSERT INTO likes (owner, postid) "
            "VALUES (?, ?) ",
            (owner,postid,)
        )
    else:
         # Query database for user's hashed password
        cur = connection.execute(
            "DELETE FROM likes "
            "WHERE owner = ? AND postid = ? ",
            (owner,postid,)
        )
    
    if target == "":
        return flask.redirect(flask.url_for('show_login'))
    else:
        return flask.redirect(flask.url_for(target))
    