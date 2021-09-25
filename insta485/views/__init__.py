"""Views, one for each Insta485 page."""
from insta485.views.index import show_index
from insta485.views.login import show_login
from insta485.views.login import account_default_redirect
from insta485.views.login import show_edit
from insta485.views.logout import logout
from insta485.views.explore import show_explore

# following page, folllower page, and follow/unfollow buttons
from insta485.views.following import show_following
from insta485.views.following import show_followers
from insta485.views.following import handle_following

from insta485.views.users import show_user
from insta485.views.posts import show_post
