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

    if len(result) == 0:
        return False

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

@insta485.app.route('/accounts/login/', methods=['GET'])
def show_login():
    """Display /login/ route."""
    if 'username' not in flask.session:
        return flask.render_template("login.html")
    return flask.redirect(flask.url_for('show_index'))


@insta485.app.route('/accounts/', methods=['POST'])
def account_default_redirect():
    target = flask.request.args.get('target')
    operation = flask.request.form['operation']
    print(target)
    print(operation)
    if target == None:
        target = flask.url_for("show_index")
    if operation == "login":
        username = flask.request.form['username']
        password = flask.request.form['password']

        if check_password(username, password):
            flask.session['username'] = flask.request.form['username']
        else:
            flask.abort(403)
        return flask.redirect(target)
    elif operation == "create":
        username = flask.request.form['username']
        password = flask.request.form['password']
        fullname = flask.request.form['fullname']
        email = flask.request.form['email']
        # file = flask.request.form['file']

        # Unpack flask object
        fileobj = flask.request.files["file"]
        filename = fileobj.filename

        # Compute base name (filename without directory).  We use a UUID to avoid
        # clashes with existing files, and ensure that the name is compatible with the
        # filesystem.
        uuid_basename = "{stem}{suffix}".format(
            stem=uuid.uuid4().hex,
            suffix=pathlib.Path(filename).suffix
        )

        # Save to disk
        path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
        fileobj.save(path)

        # get login data from database
        # Connect to database
        connection = insta485.model.get_db()
        
        #hash password
        algorithm = 'sha512'
        salt = uuid.uuid4().hex
        hash_obj = hashlib.new(algorithm)
        password_salted = salt + password
        hash_obj.update(password_salted.encode('utf-8'))
        password_hash = hash_obj.hexdigest()
        password_db_string = "$".join([algorithm, salt, password_hash])
        print(password_db_string)

        # Query database for user's hashed password
        cur = connection.execute(
            "INSERT INTO users(username, fullname, email, filename, password) "
            "VALUES (?, ?, ?, ?, ?) ",
            (username, fullname, email, filename, password,)
        )

        flask.session['username'] = username

        return flask.redirect(target)
    elif operation == "delete":

        # get login data from database
        # Connect to database
        connection = insta485.model.get_db()

        # Query database for user's hashed password
        cur = connection.execute(
            "DELETE FROM users "
            "WHERE username = ? ",
            (flask.session['username'],)
        )
        flask.session.clear()
        return flask.redirect(target)
    elif operation == "edit_account":
        username = flask.session['username']

        email = flask.request.form['email']
        fullname = flask.request.form['fullname']
        
        # Unpack flask object
        fileobj = flask.request.files["file"]
        filename = fileobj.filename

        # Compute base name (filename without directory).  We use a UUID to avoid
        # clashes with existing files, and ensure that the name is compatible with the
        # filesystem.
        uuid_basename = "{stem}{suffix}".format(
            stem=uuid.uuid4().hex,
            suffix=pathlib.Path(filename).suffix
        )

        # Save to disk
        path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
        fileobj.save(path)

        connection = insta485.model.get_db()

        # Query database for user's hashed password
        if filename != None:
            cur = connection.execute(
                "UPDATE users "
                "SET email = ?, fullname = ?, filename = ? "
                "WHERE username = ? ",
                (email, fullname, uuid_basename, username,)
            )
        else:
            cur = connection.execute(
                "UPDATE users "
                "SET email = ?, fullname = ? "
                "WHERE username = ? ",
                (email, fullname, username,)
            )
        return flask.redirect(target)
    # elif operation == "update_password":
    else:
        return flask.redirect(flask.url_for('show_index'))
    return flask.redirect(target)

@insta485.app.route('/accounts/delete/', methods=['GET'])
def show_delete():
    """Display /login/ route."""
    if 'username' in flask.session:
        context = {"logname": flask.session['username'],}
        return flask.render_template("delete.html", **context)
    return flask.redirect(flask.url_for('show_index'))

@insta485.app.route('/accounts/create/', methods=['GET'])
def show_create():
    """Display /login/ route."""
    # if 'username' not in flask.session:
    return flask.render_template("create.html")
    # return flask.redirect(flask.url_for('show_index'))

@insta485.app.route('/accounts/edit/', methods=['GET'])
def show_edit():
    """Display /login/ route."""
    if 'username' in flask.session:
        connection = insta485.model.get_db()
        username = flask.session['username']

        # Query database for user's hashed password
        cur = connection.execute(
            "SELECT fullname, email, filename "
            "FROM users "
            "WHERE username = ? ",
            (username,)
        )
        result = cur.fetchall()

        context = {"logname": username,
                    "fullname": result[0]["fullname"],
                    "email":result[0]["email"],
                    "file":result[0]["filename"]
        }
        return flask.render_template("edit.html", **context)
        # return flask.redirect(flask.url_for('show_index'))
