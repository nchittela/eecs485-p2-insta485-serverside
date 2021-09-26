"""
Insta485 index (main) view.

URLs include:
/
"""
import flask
import insta485


@insta485.app.route('/users/<user_url_slug>/')
def show_user(user_url_slug):
    """Show user."""
    if 'username' in flask.session:
        # Does page exist
        connection = insta485.model.get_db()
        cur = connection.execute(
            "SELECT fullname "
            "FROM users "
            "WHERE username = ?",
            (user_url_slug,)
        )
        if len(cur.fetchall()) == 0:
            flask.abort(404)

        logged_in = flask.session['username']

        # Query database for people following users user_url_slug
        cur = connection.execute(
            "SELECT username2 "
            "FROM following "
            "WHERE username1 = ?",
            (logged_in,)
        )
        result = cur.fetchall()

        logname_follows_username = False
        for profile in result:
            if profile["username2"] == user_url_slug:
                logname_follows_username = True
                break

        # followers
        cur = connection.execute(
            "SELECT username1 "
            "FROM following "
            "WHERE username2 = ?",
            (user_url_slug,)
        )
        result = cur.fetchall()
        followers = len(result)

        # following
        cur = connection.execute(
            "SELECT username2 "
            "FROM following "
            "WHERE username1 = ?",
            (user_url_slug,)
        )
        result = cur.fetchall()
        following = len(result)

        # fullname
        cur = connection.execute(
            "SELECT fullname "
            "FROM users "
            "WHERE username = ?",
            (user_url_slug,)
        )
        fullname = cur.fetchall()[0]['fullname']

        # posts
        cur = connection.execute(
            "SELECT filename, postid "
            "FROM posts "
            "WHERE owner = ?",
            (user_url_slug,)
        )
        posts = cur.fetchall()

        total_posts = len(posts)

        context = {"username": user_url_slug,
                   "logname": logged_in,
                   "logname_follows_username": logname_follows_username,
                   "followers": followers,
                   "following": following,
                   "fullname": fullname,
                   "posts": posts,
                   "total_posts": total_posts
                   }
        return flask.render_template("user.html", **context)
    return flask.redirect(flask.url_for("show_login"))
