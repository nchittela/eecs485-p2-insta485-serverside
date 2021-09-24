"""
Insta485 index (main) view.

URLs include:
/
"""
import flask
import insta485
app = flask.Flask(__name__)

@insta485.app.route('/')
def show_index():
    """Display / route."""

    # Connect to database
    connection = insta485.model.get_db()

    # Query database
    cur = connection.execute(
        "SELECT * FROM posts"
    )
    posts = cur.fetchall()

    # Add database info to context
    context = {"posts": posts}
    return flask.render_template("index.html", **context)

    