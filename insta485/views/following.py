"""
Insta485 index (main) view.

URLs include:
/
"""
import flask
import insta485


@insta485.app.route('/users/<user_url_slug>/following/')
def show_following(user_url_slug):
    if 'username' in flask.session:
        loggedIn = flask.session['username']
        print(user_url_slug)
        # Connect to database
        connection = insta485.model.get_db()

        # Query database for users user_url_slug is following
        cur = connection.execute(
            "SELECT username2 "
            "FROM following "
            "WHERE username1 = ?",
            (user_url_slug,)
        )
        result = cur.fetchall()

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
        userFollowing = []
        cur = connection.execute(
            "SELECT username2 "
            "FROM following "
            "WHERE username1 = ?",
            (loggedIn,)
        )
        result = cur.fetchall()

        for profile in result:
            userFollowing += [profile["username2"]]

        context = {"following":following,
                    "userFollowing": userFollowing,
                    "logname":loggedIn,
                    "currentPageUser":user_url_slug
                    }                    
        return flask.render_template("following.html", **context)
    else:
        return flask.redirect(flask.url_for('show_login'))

@insta485.app.route('/users/<user_url_slug>/followers/')
def show_followers(user_url_slug):
    if 'username' in flask.session:
        loggedIn = flask.session['username']
        # Connect to database
        connection = insta485.model.get_db()

        # Query database for people following users user_url_slug
        cur = connection.execute(
            "SELECT username1 "
            "FROM following "
            "WHERE username2 = ?",
            (user_url_slug,)
        )
        result = cur.fetchall()

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
        userFollowing = []
        cur = connection.execute(
            "SELECT username2 "
            "FROM following "
            "WHERE username1 = ?",
            (loggedIn,)
        )
        result = cur.fetchall()

        for profile in result:
            userFollowing += [profile["username2"]]

        context = {"followers":followers,
                    "userFollowing": userFollowing,
                    "logname":loggedIn,
                    "currentPageUser":user_url_slug
                    }                    
        return flask.render_template("followers.html", **context)
    else:
        context = {"following":[{"username":"Nobody"}]}
        return flask.render_template("following.html", **context)

@insta485.app.route('/following/', methods=['POST'])
def handle_following():
    target = flask.request.args.get('target')
    if target == None:
        target = flask.url_for("show_index")
    if 'username' in flask.session:
        if flask.request.form['operation'] == 'unfollow':
            connection = insta485.model.get_db()
            cur = connection.execute(
                "DELETE FROM following "
                "WHERE username1 = ? AND username2 = ?",
                (flask.session['username'], flask.request.form['username'],)
            )

            return flask.redirect(target)
        else:
            connection = insta485.model.get_db()
            cur = connection.execute(
                "INSERT INTO following (username1, username2) VALUES(?, ?)",
                (flask.session['username'], flask.request.form['username'])
            )
            return flask.redirect(target)
    else:
        return flask.redirect(flask.url_for('show_login'))
        