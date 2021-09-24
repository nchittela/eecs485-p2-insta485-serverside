"""
Insta485 index (main) view.

URLs include:
/
"""
import flask
import insta485

import uuid
import hashlib


def check_password(username, password):
    # get login data from database
    # Connect to database
    connection = insta485.model.get_db()

    # Query database for user's hashed password
    cur = connection.execute(
        "SELECT password "
        "FROM users "
        "WHERE username = ?",
        (username,)
    )
    result = cur.fetchall()
    # salted and hashed password from database
    databasePassword = result[0]['password']
    # print("DEBUG", result[0]['password'])

    # extract salt used for hashed password
    saltStart = databasePassword.index('$')+1
    saltEnd = databasePassword.index('$', saltStart)
    salt = databasePassword[saltStart:saltEnd]

    # use existing salt to hash entered password
    algorithm = 'sha512'
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])

    if password_db_string == databasePassword:
        # print("DEBUG you are logged in", username)
        return True
    return False

@insta485.app.route('/accounts/login/', methods=['GET', 'POST'])
def show_login():
    """Display /login/ route."""
    if 'username' not in flask.session:
        if flask.request.method == 'POST':
            username = flask.request.form['username']
            password = flask.request.form['password']

            if check_password(username, password):
                flask.session['username'] = flask.request.form['username']
        
            return flask.redirect(flask.url_for('show_index'))
        context = {}
        return flask.render_template("login.html", **context)
    return flask.render_template("login.html", **context)

@insta485.app.route('/temp/')
def temppage():
    if 'username' in flask.session:
        loggedIn = flask.session['username']
                # Connect to database
        connection = insta485.model.get_db()

        # Query database for user's hashed password
        cur = connection.execute(
            "SELECT username, fullname "
            "FROM users "
            "WHERE username = ?",
            (loggedIn,)
        )
        context = {"users":cur.fetchall()}
        print(context)
        return flask.render_template("temp.html", **context)
    else:
        context = {"users":[{"fullname":"Nobody"}]}
        return flask.render_template("temp.html", **context)


@insta485.app.route('/accounts/', methods=['POST'])
def account_default_redirect():
    target = flask.request.args.get('target')
    operation = flask.request.form['operation']
    print(target)
    print(operation)
    if operation == "login":
        username = flask.request.form['username']
        password = flask.request.form['password']

        if check_password(username, password):
            flask.session['username'] = flask.request.form['username']
            print(flask.session['username'])
        return flask.redirect(flask.url_for('show_index'))
    elif target == None:
        return flask.redirect(flask.url_for('show_index'))
    return flask.redirect(flask.request.args.get('target'))