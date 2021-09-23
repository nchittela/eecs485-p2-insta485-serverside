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
        "SELECT * FROM comments" 
    )
    posts = cur.fetchall()

    # Add database info to context
    context = {"posts": posts}
    return flask.render_template("index.html", **context)

@insta485.app.route('/login/', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'POST':
        print("DEBUG", flask.request.form['username'])
        flask.session['username'] = flask.request.form['username']
        return flask.redirect(flask.url_for('index'))
    return '''
    <form action="" method="post">
      <p><input type=text name=username>
      <p><input type=submit value=Login>
    </form>'''


@insta485.app.route('/logout/')
def logout():
    flask.session.clear()
    return flask.redirect(flask.url_for('index'))



    