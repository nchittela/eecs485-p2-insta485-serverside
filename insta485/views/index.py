"""
Insta485 index (main) view.

URLs include:
/
"""
import flask
import arrow
import insta485
app = flask.Flask(__name__)


@insta485.app.route('/')
def show_index():
    """Display / route."""
    if 'username' in flask.session:
        logged_in = flask.session['username']

        # Connect to database
        connection = insta485.model.get_db()

        # people following
        cur = connection.execute(
            "SELECT username2 "
            "FROM following "
            "WHERE username1 = ? ",
            (logged_in,)
        )
        result = cur.fetchall()

        all_posts = []

        for following in result:
            cur = connection.execute(
                "SELECT owner, postid, filename, created "
                "FROM posts "
                "WHERE owner = ? ",
                (following['username2'],)
            )
            posts = cur.fetchall()
            all_posts += posts

        cur = connection.execute(
            "SELECT owner, postid, filename, created "
            "FROM posts "
            "WHERE owner = ? ",
            (logged_in,)
        )
        posts = cur.fetchall()
        all_posts += posts

        for i, apost in enumerate(all_posts):
            # print(all_posts[i]['created'])

            human = arrow.get(apost['created']).humanize()
            all_posts[i]['timestamp'] = human

            cur = connection.execute(
                "SELECT likeid "
                "FROM likes "
                "WHERE postid = ? ",
                (all_posts[i]['postid'],)
            )
            all_posts[i]['likes'] = len(cur.fetchall())

            cur = connection.execute(
                "SELECT commentid, text, owner, created "
                "FROM comments "
                "WHERE postid = ? "
                "ORDER BY created ASC ",
                (all_posts[i]['postid'],)
            )
            all_posts[i]['comments'] = cur.fetchall()

            all_posts[i]['liked'] = False
            cur = connection.execute(
                "SELECT likeid "
                "FROM likes "
                "WHERE owner = ? AND postid = ? ",
                (logged_in, all_posts[i]['postid'],)
            )
            if len(cur.fetchall()) > 0:
                all_posts[i]['liked'] = True

            cur = connection.execute(
                "SELECT filename "
                "FROM users "
                "WHERE username = ? ",
                (all_posts[i]['owner'],)
            )
            all_posts[i]['owner_img_url'] = cur.fetchall()[0]['filename']

        all_posts.sort(key=lambda x: x['postid'], reverse=True)

        context = {"logname": logged_in,
                   "posts": all_posts
                   }
        return flask.render_template("index.html", **context)

    return flask.redirect(flask.url_for('show_login'))


@insta485.app.route('/uploads/<filename>')
def check_file(filename):
    """Check file."""
    if 'username' not in flask.session:
        flask.abort(403)
    else:
        # Connect to database
        connection = insta485.model.get_db()

        # people following
        cur = connection.execute(
            "SELECT * "
            "FROM posts "
            "WHERE filename = ? ",
            (filename,)
        )

        if len(cur.fetchall()) == 0:
            flask.abort(404)
    folder = insta485.app.config["UPLOAD_FOLDER"]
    return flask.send_from_directory(folder, filename)
