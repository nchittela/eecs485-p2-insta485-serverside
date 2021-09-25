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
            "ORDER BY commentid DESC ",
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