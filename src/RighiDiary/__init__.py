__all__ = (
    "Agenda",
    "User",
    "Homework",
    "Schedule",
    "AuthResponse",
    "fast_auth",
    "authorize_user",
    "get_user_agenda",
    "get_user_homework",
    "get_user_schedule",
    "get_user_marks",
)

__version__ = "0.0.9"
__logger__ = "RighiDiary"

from ._user import User
from ._auth_functions import (
    AuthResponse,
    fast_auth,
)
from ._authorize_user import authorize_user
from ._agenda import Agenda, get_user_agenda
from ._homework import Homework, get_user_homework
from ._schedule import Schedule, get_user_schedule
from ._marks import Mark, get_user_marks
