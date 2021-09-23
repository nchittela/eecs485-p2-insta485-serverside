"""
Insta485 index (main) view.

URLs include:
/
"""
import flask
import insta485


@insta485.app.route('/<user_url_slug>/following/', methods=['GET', 'POST'])
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


        print(userFollowing)

        context = {"following":following,
                    "userFollowing": userFollowing,
                    "logname":loggedIn,
                    "currentPageUser":user_url_slug
                    }                    
        return flask.render_template("following.html", **context)
    else:
        context = {"following":[{"username":"Nobody"}]}
        return flask.render_template("following.html", **context)

@insta485.app.route('/following/', methods=['POST'])
def handle_following():
    if 'username' in flask.session:
        if flask.request.form['operation'] == 'unfollow':
            print("unfollowing " + flask.request.args.get('target'))

            connection = insta485.model.get_db()
            cur = connection.execute(
                "DELETE FROM following "
                "WHERE username1 = ? AND username2 = ?",
                (flask.session['username'], flask.request.form['username'],)
            )
            print(flask.session['username'])
            print(flask.request.form['username'] +"a")
            print(flask.request.form['unfollow'])
            print(flask.request.form['operation'])
            
            return flask.redirect(flask.request.args.get('target'))
        else:
            print("following person")
            connection = insta485.model.get_db()
            cur = connection.execute(
                "INSERT INTO following (username1, username2) VALUES(?, ?)",
                (flask.session['username'], flask.request.form['username'])
            )
            return flask.redirect(flask.request.args.get('target'))
    else:
        print("Not signed in")