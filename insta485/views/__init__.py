"""Views, one for each Insta485 page."""
from insta485.views.index import show_index
from insta485.views.login import show_login
from insta485.views.login import temppage
from insta485.views.logout import logout

# following page, folllower page, and follow/unfollow buttons
from insta485.views.following import show_following
from insta485.views.following import show_followers
from insta485.views.following import handle_following