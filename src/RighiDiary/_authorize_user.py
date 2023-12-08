import asyncio
from typing import Union

from ._agenda import get_user_agenda
from ._auth_functions import fast_auth, get_user_data, UserData
from ._user import User
from ._homework import get_user_homework
from ._schedule import get_user_schedule
from ._marks import get_user_marks


async def authorize_user(login: int, password: str) -> Union[User, None]:
    auth_response = await fast_auth(login=login, password=password)
    if not auth_response:
        return None

    tasks = [
        asyncio.create_task(
            get_user_data(
                PHPSESSID_cookie=auth_response.PHPSESSID_cookie,
                messenger_cookie=auth_response.messenger_cookie,
            )
        ),
        asyncio.create_task(get_user_agenda(login=login, password=password)),
        asyncio.create_task(get_user_homework(login=login, password=password)),
        asyncio.create_task(get_user_schedule(login=login, password=password)),
        asyncio.create_task(get_user_marks(login=login, password=password)),
    ]

    response = await asyncio.gather(*tasks)

    current_key = None
    mastercom_id = None
    name = None
    surname = None
    classes = None
    phone = None
    email = None

    if auth_response is not None:
        current_key = auth_response.current_key
        mastercom_id = auth_response.mastercom_id

    user_data_response: UserData = response[0]
    if user_data_response:
        name = user_data_response.name
        surname = user_data_response.surname
        classes = user_data_response.classes
        phone = user_data_response.phone
        email = user_data_response.email

    agenda_response = response[1]
    homework_response = response[2]
    schedule_response = response[3]
    marks_response = response[4]

    user = User(
        login=login,
        password=password,
        name=name,
        surname=surname,
        classes=classes,
        phone=phone,
        email=email,
        current_key=current_key,
        mastercom_id=mastercom_id,
        agenda=agenda_response,
        homework=homework_response,
        schedule=schedule_response,
        marks=marks_response,
    )

    return user
