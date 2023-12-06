__version__ = "0.0.2"
__logger__ = "RighiDiary"

from ._user import User
from ._auth_functions import (
    AuthData,
    fast_auth,
    get_current_key,
)
from ._authorize_user import authorize_user
from ._agenda import Agenda, get_user_agenda
