import aiohttp
import re
import logging
from bs4 import BeautifulSoup
from typing import Union

from . import __logger__

logger = logging.getLogger(__logger__ + ".Auth")


class AuthData:
    def __init__(
        self,
        messenger_cookie: str,
        PHPSESSID_cookie: str,
        current_key: str,
        user_id: int,
    ):
        self.messenger_cookie = messenger_cookie
        self.PHPSESSID_cookie = PHPSESSID_cookie
        self.current_key = current_key
        self.user_id = user_id


class UserData:
    def __init__(
        self,
        name: str,
        surname: str,
        mastercom_id: int,
        classes: str,
        email: Union[str, None],
        phone: Union[str, None],
    ):
        self.name = name
        self.surname = surname
        self.mastercom_id = mastercom_id
        self.classes = classes
        self.email = email
        self.phone = phone


async def get_user_data(
    messenger_cookie: str, PHPSESSID_cookie: str
) -> Union[UserData, bool]:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            url="https://righi-fc.registroelettronico.com/messenger/1.0/authentication",
            headers={
                "Cookie": f"messenger={messenger_cookie}; PHPSESSID={PHPSESSID_cookie}"
            },
        ) as resp:
            if resp.status != 200 or not (resp_json := await resp.json())["success"]:
                return False
            else:
                results = resp_json["results"]

                if results:
                    try:
                        properties = results["properties"]

                        name = properties["name"]
                        surname = properties["surname"]
                        mastercom_id = properties["code"]
                        classes = properties["classes"]
                        email = properties["email"] if properties["email"] else None
                        phone = properties["phone"] if properties["phone"] else None
                    except:
                        logger.debug(
                            msg="Error when processing a response to retrieve user data!"
                        )
                        return False
                    else:
                        user_data = UserData(
                            name, surname, mastercom_id, classes, email, phone
                        )
                        return user_data


async def get_PHPSESSID_cookie():
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://righi-fc.registroelettronico.com/mastercom/"
        ) as resp:
            match = re.search(r"PHPSESSID=([^;]+)", str(resp.cookies["PHPSESSID"]))
            if match:
                return match.group(1)
            else:
                logger.debug(msg="Error when receiving PHPSESSID cookie!")
                return False


async def get_messenger_cookie(PHPSESSID_cookie: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://righi-fc.registroelettronico.com/messenger/1.0/authentication",
            headers={"Cookie": f"PHPSESSID={PHPSESSID_cookie}"},
        ) as resp:
            match = re.search(r"messenger=([^;]+)", str(resp.cookies["messenger"]))
            if match:
                return match.group(1)
            else:
                logger.debug(msg="Error when receiving messenger cookie!")
                return False


async def authorization(PHPSESSID_cookie: str, messenger_cookie: str, current_key: str):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            url=f"https://righi-fc.registroelettronico.com/messenger/1.0/login/{current_key}",
            headers={
                "Cookie": f"PHPSESSID={PHPSESSID_cookie}; messenger={messenger_cookie}"
            },
        ) as resp:
            if resp.status != 200:
                logger.debug(msg="Error during cookie authorisation!")
                return False
            else:
                return True


async def get_current_key(
    PHPSESSID_cookie: str, messenger_cookie: str, password: str, login: int
) -> Union[str, None]:
    async with aiohttp.ClientSession() as session:
        async with session.post(
            url="https://righi-fc.registroelettronico.com/mastercom/index.php",
            headers={
                "Cookie": f"PHPSESSID={PHPSESSID_cookie}; messenger={messenger_cookie}"
            },
            data={"user": str(login), "password_user": password, "form_login": "true"},
        ) as resp:
            if resp.status != 200:
                logger.debug(msg="Error when obtaining the current key!")
                return None
            else:
                soup = BeautifulSoup(await resp.text(), "html.parser")

                try:
                    current_key = soup.find("input", {"id": "current_key"})["value"]
                except:
                    logger.debug(msg="Error when obtaining the current key!")
                    return None

                return current_key if current_key else None


async def fast_auth(
    password: str = None, login: int = None, current_key: str = None
) -> Union[AuthData, None]:
    if current_key is None and password is None and login is None:
        return None

    if not (PHPSESSID_cookie := await get_PHPSESSID_cookie()):
        return None

    if not (
        messenger_cookie := await get_messenger_cookie(
            PHPSESSID_cookie=PHPSESSID_cookie
        )
    ):
        return None

    if current_key is None:
        current_key = await get_current_key(
            PHPSESSID_cookie=PHPSESSID_cookie,
            messenger_cookie=messenger_cookie,
            password=password,
            login=login,
        )

    status = await authorization(
        PHPSESSID_cookie=PHPSESSID_cookie,
        messenger_cookie=messenger_cookie,
        current_key=current_key,
    )
    if not status:
        logger.debug(f"Auth status: {status}")
        return None

    response = await get_user_data(
        messenger_cookie=messenger_cookie, PHPSESSID_cookie=PHPSESSID_cookie
    )
    if not response:
        logger.debug(msg="Error when retrieving user data!")
        return None

    if not response.mastercom_id:
        logger.debug(msg="Absence of mastercom id on response!")
        return None

    auth_data = AuthData(
        messenger_cookie=messenger_cookie,
        PHPSESSID_cookie=PHPSESSID_cookie,
        current_key=current_key,
        user_id=response.mastercom_id,
    )

    return auth_data
