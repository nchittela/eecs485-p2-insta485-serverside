"""
Insta485 index (main) view.

URLs include:
/
"""
import flask
import insta485


@insta485.app.route('/explore/')
def show_explore():
    """Show explore."""
    if 'username' in flask.session:
        logged_in = flask.session['username']
        # Connect to database
        connection = insta485.model.get_db()

        # Query database for people the user is following
        cur2 = connection.execute(
            "SELECT username2 "
            "FROM following "
            "WHERE username1 = ?",
            (logged_in,)
        )
        result = cur2.fetchall()

        following = []
        for profile in result:
            following += [profile['username2']]

        # Query database for all users
        cur = connection.execute(
            "SELECT username, filename "
            "FROM users "
        )
        result = cur.fetchall()

        context = {"following": following,
                   "allUsers": result,
                   "logname": logged_in
                   }
        return flask.render_template("explore.html", **context)
    return flask.redirect(flask.url_for("show_login"))
