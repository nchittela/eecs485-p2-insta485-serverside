"""
Insta485 index (main) view.

URLs include:
/
"""
import flask
import insta485


@insta485.app.route('/users/<user_url_slug>/following/')
def show_following(user_url_slug):
    """Show following."""
    if 'username' in flask.session:
        logged_in = flask.session['username']
        print(user_url_slug)
        # Connect to database
        connection = insta485.model.get_db()

        # Query database for users user_url_slug is following
        cur5 = connection.execute(
            "SELECT username2 "
            "FROM following "
            "WHERE username1 = ?",
            (user_url_slug,)
        )
        result = cur5.fetchall()

        cur2 = connection.execute(
            "SELECT fullname "
            "FROM users "
            "WHERE username = ?",
            (user_url_slug,)
        )
        if len(cur2.fetchall()) == 0:
            flask.abort(404)

        # get detailed profile of people
        # user_url_slug is following
        following = []
        for profile in result:
            cur = connection.execute(
                "SELECT username, filename "
                "FROM users "
                "WHERE username = ?",
                (profile["username2"],)
            )
            result = cur.fetchall()
            following += result

        # Query database for anyone user is following
        user_following = []
        cur6 = connection.execute(
            "SELECT username2 "
            "FROM following "
            "WHERE username1 = ?",
            (logged_in,)
        )
        result = cur6.fetchall()

        for profile in result:
            user_following += [profile["username2"]]

        context = {"following": following,
                   "userFollowing": user_following,
                   "logname": logged_in,
                   "currentPageUser": user_url_slug
                   }
        return flask.render_template("following.html", **context)
    return flask.redirect(flask.url_for('show_login'))


@insta485.app.route('/users/<user_url_slug>/followers/')
def show_followers(user_url_slug):
    """Show followers."""
    if 'username' in flask.session:
        logged_in = flask.session['username']
        # Connect to database
        connection = insta485.model.get_db()

        # Query database for people following users user_url_slug
        cur4 = connection.execute(
            "SELECT username1 "
            "FROM following "
            "WHERE username2 = ?",
            (user_url_slug,)
        )
        result = cur4.fetchall()

        cur3 = connection.execute(
            "SELECT fullname "
            "FROM users "
            "WHERE username = ?",
            (user_url_slug,)
        )
        if len(cur3.fetchall()) == 0:
            flask.abort(404)

        # get detailed profile of people following user_url_slug
        followers = []
        for profile in result:
            cur = connection.execute(
                "SELECT username, filename "
                "FROM users "
                "WHERE username = ?",
                (profile["username1"],)
            )
            result = cur.fetchall()
            followers += result

        # Query database for anyone following user
        user_following = []
        cur7 = connection.execute(
            "SELECT username2 "
            "FROM following "
            "WHERE username1 = ?",
            (logged_in,)
        )
        result = cur7.fetchall()

        for profile in result:
            user_following += [profile["username2"]]

        context = {"followers": followers,
                   "userFollowing": user_following,
                   "logname": logged_in,
                   "currentPageUser": user_url_slug
                   }
        return flask.render_template("followers.html", **context)
    return flask.redirect(flask.url_for('show_login'))


@insta485.app.route('/following/', methods=['POST'])
def handle_following():
    """Handle following."""
    target = flask.request.args.get('target')
    if target is None:
        target = flask.url_for("show_index")
    if 'username' in flask.session:
        if flask.request.form['operation'] == 'unfollow':
            connection = insta485.model.get_db()
            cur = connection.execute(
                "SELECT created "
                "FROM following "
                "WHERE username1 = ? AND username2 = ? ",
                (flask.session['username'], flask.request.form['username'],)
            )
            if(len(cur.fetchall())) == 0:
                flask.abort(409)

            cur = connection.execute(
                "DELETE FROM following "
                "WHERE username1 = ? AND username2 = ?",
                (flask.session['username'], flask.request.form['username'],)
            )
        else:
            connection = insta485.model.get_db()

            cur = connection.execute(
                "SELECT created "
                "FROM following "
                "WHERE username1 = ? AND username2 = ? ",
                (flask.session['username'], flask.request.form['username'],)
            )
            if(len(cur.fetchall())) != 0:
                flask.abort(409)

            cur = connection.execute(
                "INSERT INTO following (username1, username2) VALUES(?, ?)",
                (flask.session['username'], flask.request.form['username'])
            )
        return flask.redirect(target)
    return flask.redirect(flask.url_for('show_login'))
