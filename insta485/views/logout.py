"""
Insta485 index (main) view.

URLs include:
/
"""
import flask
import insta485


@insta485.app.route('/accounts/logout/')
def logout():
  flask.session.clear()
  return flask.redirect(flask.url_for('show_index'))