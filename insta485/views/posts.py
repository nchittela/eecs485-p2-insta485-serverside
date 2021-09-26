"""
Insta485 index (main) view.

URLs include:
/
"""
import uuid
import pathlib
import os
import flask
import arrow
import insta485


@insta485.app.route('/likes/', methods=['POST'])
def do_likes():
    """Do likes."""
    target = flask.request.args.get('target')
    operation = flask.request.form['operation']
    owner = flask.session['username']
    postid = flask.request.form['postid']

    # get login data from database
    # Connect to database
    connection = insta485.model.get_db()

    if operation == 'like':
        # check fr duplicate like
        cur = connection.execute(
            "SELECT owner, postid "
            "FROM likes "
            "Where owner = ? AND postid = ? ",
            (owner, postid,)
        )
        if len(cur.fetchall()) == 1:
            flask.abort(409)
        # Query database for user's hashed password
        cur = connection.execute(
            "INSERT INTO likes (owner, postid) "
            "VALUES (?, ?) ",
            (owner, postid,)
        )
    else:
        # check for duplicate unlike
        cur = connection.execute(
            "SELECT owner, postid "
            "FROM likes "
            "Where owner = ? AND postid = ? ",
            (owner, postid,)
        )
        if len(cur.fetchall()) == 0:
            flask.abort(409)

        # Query database for user's hashed password
        cur = connection.execute(
            "DELETE FROM likes "
            "WHERE owner = ? AND postid = ? ",
            (owner, postid,)
        )

    if target is None:
        return flask.redirect(flask.url_for('show_login'))
    return flask.redirect(target)


@insta485.app.route('/posts/<postid_url_slug>/', methods=['GET'])
def show_post(postid_url_slug):
    """Show post."""
    print('username' in flask.session)

    if 'username' in flask.session:
        logged_in = flask.session['username']

        # Connect to database
        connection = insta485.model.get_db()

        # Query database for people following users user_url_slug
        cur = connection.execute(
            "SELECT owner "
            "FROM posts "
            "WHERE postid = ?",
            (postid_url_slug,)
        )
        owner = cur.fetchall()[0]["owner"]

        # owner_img_url
        cur = connection.execute(
            "SELECT filename "
            "FROM users "
            "WHERE username = ?",
            (owner,)
        )
        owner_img_url = cur.fetchall()[0]["filename"]

        # img_url
        cur = connection.execute(
            "SELECT filename "
            "FROM posts "
            "WHERE postid = ?",
            (postid_url_slug,)
        )
        img_url = cur.fetchall()[0]["filename"]

        # likes
        cur = connection.execute(
            "SELECT likeid "
            "FROM likes "
            "WHERE postid = ?",
            (postid_url_slug,)
        )
        likes = len(cur.fetchall())

        # comments
        cur = connection.execute(
            "SELECT text, owner, commentid "
            "FROM comments "
            "WHERE postid = ? "
            "ORDER BY commentid ASC ",
            (postid_url_slug,)
        )
        comments = cur.fetchall()

        # liked
        liked = False
        cur = connection.execute(
            "SELECT likeid "
            "FROM likes "
            "WHERE owner = ? AND postid = ? ",
            (logged_in, postid_url_slug,)
        )
        if len(cur.fetchall()) > 0:
            liked = True

        # post timestamp
        cur = connection.execute(
            "SELECT created "
            "FROM posts "
            "WHERE postid = ? ",
            (postid_url_slug,)
        )
        timestamp = cur.fetchall()[0]["created"]

        timestamp = arrow.get(timestamp).humanize()

        context = {"logname": logged_in,
                   "owner": owner,
                   "owner_img_url": owner_img_url,
                   "postid": postid_url_slug,
                   "img_url": img_url,
                   "likes": likes,
                   "comments": comments,
                   "liked": liked,
                   "timestamp": timestamp
                   }
        return flask.render_template("post.html", **context)
    return flask.redirect(flask.url_for('show_login'))


@insta485.app.route('/comments/', methods=['POST'])
def do_comment():
    """Do comment."""
    if 'username' in flask.session:
        logged_in = flask.session['username']
        operation = flask.request.form['operation']
        target = flask.request.args.get('target')

        # Connect to database
        connection = insta485.model.get_db()

        if flask.request.form == "":
            flask.abort(400)

        if operation == 'create':
            # Query database for people following users user_url_slug
            cur = connection.execute(
                "INSERT INTO comments(owner, postid, text) "
                "VALUES (?, ?, ?) ",
                (logged_in, flask.request.form['postid'],
                 flask.request.form['text'],)
            )
        else:
            cur = connection.execute(
                "SELECT owner "
                "FROM comments "
                "WHERE commentid = ? ",
                (flask.request.form['commentid'],)
            )
            if cur.fetchall()[0]['owner'] != logged_in:
                flask.abort(403)

            cur = connection.execute(
                "DELETE FROM comments "
                "WHERE commentid = ? ",
                (flask.request.form['commentid'],)
            )
        if target is None:
            return flask.redirect(flask.url_for('show_index'))
        return flask.redirect(target)
    return flask.redirect(flask.url_for('show_login'))


@insta485.app.route('/posts/', methods=['POST'])
def do_post():
    """Do post."""
    if 'username' in flask.session:
        logged_in = flask.session['username']
        operation = flask.request.form['operation']
        target = flask.request.args.get('target')

        # Connect to database
        connection = insta485.model.get_db()

        if operation == 'create':
            if flask.request.files['file'] is None:
                flask.abort(400)

            # Unpack flask object
            fileobj2 = flask.request.files["file"]
            filename = fileobj2.filename

            uuid_basename = "{stem}{suffix}".format(
                stem=uuid.uuid4().hex,
                suffix=pathlib.Path(filename).suffix
            )

            # Save to disk
            path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
            fileobj2.save(path)

            # Query database for people following users user_url_slug
            cur = connection.execute(
                "INSERT INTO posts(filename, owner) "
                "VALUES (?, ?) ",
                (uuid_basename, logged_in,)
            )
        else:
            cur = connection.execute(
                "SELECT owner "
                "FROM posts "
                "WHERE postid = ? ",
                (flask.request.form['postid'],)
            )
            if cur.fetchall()[0]['owner'] != logged_in:
                flask.abort(403)

            cur = connection.execute(
                "SELECT filename FROM posts "
                "WHERE postid = ? ",
                (flask.request.form['postid'],)
            )
            result = cur.fetchall()[0]['filename']
            path = insta485.app.config["UPLOAD_FOLDER"]/result

            os.remove(path)

            cur = connection.execute(
                "DELETE FROM posts "
                "WHERE postid = ? ",
                (flask.request.form['postid'],)
            )
        if target is None:
            url = flask.url_for('show_user', user_url_slug=logged_in)
            return flask.redirect(url)
        return flask.redirect(target)
    return flask.redirect(flask.url_for('show_login'))
