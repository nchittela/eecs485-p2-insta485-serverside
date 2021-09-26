"""
Insta485 index (main) view.

URLs include:
/
"""
from re import I
import flask
import insta485

import uuid
import hashlib
import pathlib
import os

import arrow

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
        # check fr duplicate like
        cur = connection.execute(
            "SELECT owner, postid "
            "FROM likes "
            "Where owner = ? AND postid = ? ",
            (owner,postid,)
        )
        if len(cur.fetchall()) == 1:
            flask.abort(409)
        # Query database for user's hashed password
        cur = connection.execute(
            "INSERT INTO likes (owner, postid) "
            "VALUES (?, ?) ",
            (owner,postid,)
        )
    else:
        #check for duplicate unlike
        cur = connection.execute(
            "SELECT owner, postid "
            "FROM likes "
            "Where owner = ? AND postid = ? ",
            (owner,postid,)
        )
        if len(cur.fetchall()) == 0:
            flask.abort(409)
        
         # Query database for user's hashed password
        cur = connection.execute(
            "DELETE FROM likes "
            "WHERE owner = ? AND postid = ? ",
            (owner,postid,)
        )
    
    if target == None:
        return flask.redirect(flask.url_for('show_login'))
    else:
        return flask.redirect(target)
    
@insta485.app.route('/posts/<postid_url_slug>/', methods=['GET'])
def show_post(postid_url_slug):
    print('username' in flask.session)

    if 'username' in flask.session:
        loggedIn = flask.session['username']

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
            (loggedIn,postid_url_slug,)
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
        

        context = {
            "logname":loggedIn,
            "owner":owner,
            "owner_img_url":owner_img_url,
            "postid" : postid_url_slug,
            "img_url": img_url,
            "likes": likes,
            "comments": comments,
            "liked": liked,
            "timestamp": timestamp


        }
        return flask.render_template("post.html", **context)
    else:
        return flask.redirect(flask.url_for('show_login'))


@insta485.app.route('/comments/', methods=['POST'])
def do_comment():
    if 'username' in flask.session:
        loggedIn = flask.session['username']
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
                (loggedIn, flask.request.form['postid'], flask.request.form['text'],)
            )
        else:
            cur = connection.execute(
                "SELECT owner "
                "FROM comments "
                "WHERE commentid = ? ",
                (flask.request.form['commentid'],)
            )
            if(cur.fetchall()[0]['owner'] != loggedIn):
                flask.abort(403)

            cur = connection.execute(
                "DELETE FROM comments "
                "WHERE commentid = ? ",
                (flask.request.form['commentid'],)
            )
        if target == None:
            return flask.redirect(flask.url_for('show_index'))
        else:
            return flask.redirect(target)
    else:
        return flask.redirect(flask.url_for('show_login'))

@insta485.app.route('/posts/', methods=['POST'])
def do_post():
    if 'username' in flask.session:
        loggedIn = flask.session['username']
        operation = flask.request.form['operation']
        target = flask.request.args.get('target')
        

        # Connect to database
        connection = insta485.model.get_db()

        if operation == 'create':
            if flask.request.files['file'] == None:
                flask.abort(400)

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
            
            # Query database for people following users user_url_slug
            cur = connection.execute(
                "INSERT INTO posts(filename, owner) "
                "VALUES (?, ?) ",
                (uuid_basename, loggedIn,)
            )
        else:
            cur = connection.execute(
                "SELECT owner "
                "FROM posts "
                "WHERE postid = ? ",
                (flask.request.form['postid'],)
            )
            if(cur.fetchall()[0]['owner'] != loggedIn):
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
        if target == None:
            return flask.redirect(flask.url_for('show_user', user_url_slug = loggedIn))
        else:
            return flask.redirect(target)
    else:
        return flask.redirect(flask.url_for('show_login'))