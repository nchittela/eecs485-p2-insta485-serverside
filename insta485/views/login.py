"""
Insta485 index (main) view.

URLs include:
/
"""
import uuid
import hashlib
import pathlib
import flask
import insta485


def check_password(username, password):
    """Check pass."""
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
    database_password = result[0]['password']
    # print("DEBUG", result[0]['password'])

    # extract salt used for hashed password
    salt_start = database_password.index('$')+1
    salt_end = database_password.index('$', salt_start)
    salt = database_password[salt_start:salt_end]

    # use existing salt to hash entered password
    algorithm = 'sha512'
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])

    if password_db_string == database_password:
        # print("DEBUG you are logged in", username)
        return True
    return False


def create_function():
    """Create function."""
    username = flask.request.form['username']
    password = flask.request.form['password']
    fullname = flask.request.form['fullname']
    email = flask.request.form['email']
    got_file = flask.request.files['file']

    if username == "" or password == "":
        flask.abort(400)

    if fullname == "" or email == "" or got_file == "":
        flask.abort(400)

    connection = insta485.model.get_db()

    # Query database for user's hashed password
    cur = connection.execute(
        "SELECT * "
        "FROM users "
        "WHERE username = ?",
        (username,)
    )
    if len(cur.fetchall()) != 0:
        flask.abort(409)

    # Unpack flask object
    fileobj = flask.request.files["file"]
    filename = fileobj.filename

    uuid_basename = "{stem}{suffix}".format(
        stem=uuid.uuid4().hex,
        suffix=pathlib.Path(filename).suffix
    )

    # Save to disk
    path2 = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
    fileobj.save(path2)

    # get login data from database
    # Connect to database
    connection = insta485.model.get_db()

    # hash password
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new('sha512')
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_db_string = "$".join(['sha512', salt, hash_obj.hexdigest()])
    print(password_db_string)

    # Query database for user's hashed password
    connection.execute(
        "INSERT INTO users(username, fullname, email, filename, password) "
        "VALUES (?, ?, ?, ?, ?) ",
        (username, fullname, email, filename, password_db_string,)
        )

    flask.session['username'] = username


@insta485.app.route('/accounts/login/', methods=['GET'])
def show_login():
    """Display /login/ route."""
    if 'username' not in flask.session:
        return flask.render_template("login.html")
    return flask.redirect(flask.url_for('show_index'))


def edit_account_function():
    """Edit func."""
    if 'username' not in flask.session:
        flask.abort(403)

    username = flask.session['username']

    this_email = flask.request.form['email']
    fullname = flask.request.form['fullname']

    if this_email == "" or fullname == "":
        flask.abort(400)

    connection = insta485.model.get_db()

    # Unpack flask object
    fileobj = flask.request.files["file"]
    filename = fileobj.filename

    uuid_basename = "{stem}{suffix}".format(
        stem=uuid.uuid4().hex,
        suffix=pathlib.Path(filename).suffix
    )

    # Save to disk
    path3 = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
    fileobj.save(path3)

    # Query database for user's hashed password
    if filename is not None:
        connection.execute(
            "UPDATE users "
            "SET email = ?, fullname = ?, filename = ? "
            "WHERE username = ? ",
            (this_email, fullname, uuid_basename, username,)
        )
    else:
        connection.execute(
            "UPDATE users "
            "SET email = ?, fullname = ? "
            "WHERE username = ? ",
            (this_email, fullname, username,)
        )


def login_function():
    """Login func."""
    username = flask.request.form['username']
    password = flask.request.form['password']

    if username == "" or password == "":
        flask.abort(400)

    if check_password(username, password):
        flask.session['username'] = flask.request.form['username']
    else:
        flask.abort(403)


def delete_function():
    """Delete func."""
    if 'username' not in flask.session:
        flask.abort(403)

    # get login data from database
    # Connect to database
    connection = insta485.model.get_db()

    # Query database for user's hashed password
    connection.execute(
        "DELETE FROM users "
        "WHERE username = ? ",
        (flask.session['username'],)
    )
    flask.session.clear()


@insta485.app.route('/accounts/', methods=['POST'])
def account_default_redirect():
    """Account stuff."""
    target = flask.request.args.get('target')
    operation = flask.request.form['operation']
    print(target)
    print(operation)
    if target is None:
        target = flask.url_for("show_index")
    if operation == "login":
        login_function()
    elif operation == "create":
        create_function()
        return flask.redirect(target)
    elif operation == "delete":
        delete_function()
    elif operation == "edit_account":
        edit_account_function()
    elif operation == "update_password":
        if 'username' not in flask.session:
            flask.abort(403)

        username = flask.session['username']
        old_password = flask.request.form['password']
        new_password1 = flask.request.form['new_password1']
        new_password2 = flask.request.form['new_password2']

        if old_password == "" or new_password1 == "" or new_password2 == "":
            flask.abort(400)

        if not check_password(username, old_password):
            flask.abort(403)

        if new_password1 == new_password2:
            algorithm = 'sha512'
            salt = uuid.uuid4().hex
            hash_obj = hashlib.new(algorithm)
            password_salted = salt + new_password1
            hash_obj.update(password_salted.encode('utf-8'))
            password_hash = hash_obj.hexdigest()
            password_db_string = "$".join([algorithm, salt, password_hash])
            print(password_db_string)

            connection = insta485.model.get_db()

            connection.execute(
                "UPDATE users "
                "SET password = ? "
                "WHERE username = ? ",
                (password_db_string, username,)
            )
        else:
            flask.abort(401)

        return flask.redirect(target)
    else:
        return flask.redirect(flask.url_for('show_index'))
    return flask.redirect(target)


@insta485.app.route('/accounts/delete/', methods=['GET'])
def show_delete():
    """Display /login/ route."""
    if 'username' in flask.session:
        context = {"logname": flask.session['username']}
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
                   "email": result[0]["email"],
                   "file": result[0]["filename"]
                   }
        return flask.render_template("edit.html", **context)
    return flask.redirect(flask.url_for('show_index'))


@insta485.app.route('/accounts/password/', methods=['GET'])
def show_password():
    """Display /login/ route."""
    if 'username' in flask.session:
        username = flask.session['username']

        context = {"logname": username,
                   }
        return flask.render_template("password.html", **context)
    return flask.redirect(flask.url_for('show_index'))
