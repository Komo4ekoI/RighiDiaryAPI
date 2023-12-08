import logging
from typing import List, Union
import datetime
import aiohttp
from bs4 import BeautifulSoup

from . import __logger__
from . import _auth_functions

logger = logging.getLogger(__logger__ + ".Mark")


class Mark:
    def __init__(
        self,
        subject_name: str,
        assessment: str,
        description: str,
        receiver_for: str,
        date: datetime.date,
        notification: bool,
        notification_type: Union[str, None],
    ):
        self.subject_name = subject_name
        self.assessment = assessment
        self.description = description if description else None
        self.receiver_for = receiver_for
        self.date = date
        self.notification = notification
        self.notification_type = notification_type

    def __str__(self):
        attributes = ", ".join(f"{key}={value}" for key, value in vars(self).items())
        return f"{self.__class__.__name__}({attributes})"


async def get_user_marks(
    login: int,
    password: str,
    PHPSESSID_cookie: str = None,
    messenger_cookie: str = None,
    current_key: str = None,
    user_id: int = None,
) -> Union[List[Mark], None]:
    if not PHPSESSID_cookie or not messenger_cookie or not current_key or not user_id:
        response = await _auth_functions.fast_auth(password=password, login=login)

        if not response:
            logger.debug(msg="An error occurred when authorising to receive Marks!")
            return None

        PHPSESSID_cookie = response.PHPSESSID_cookie
        messenger_cookie = response.PHPSESSID_cookie
        current_key = response.current_key
        user_id = response.mastercom_id

    async with aiohttp.ClientSession() as session:
        async with session.post(
            url="https://righi-fc.registroelettronico.com/mastercom/index.php",
            headers={
                "Cookie": f"PHPSESSID={PHPSESSID_cookie}; messenger={messenger_cookie}"
            },
            data={
                "form_stato": "studente",
                "stato_principale": "voti",
                "stato_secondario": "",
                "permission": "",
                "operazione": "",
                "current_user": str(user_id),
                "current_key": current_key,
                "from_app": "",
                "header": "SI",
            },
        ) as resp:
            if resp.status != 200:
                logger.debug(msg=f"Error on receipt of Marks. Status: {resp.status}")
                return None
            else:
                try:
                    soup = BeautifulSoup(await resp.text(), features="html.parser")
                    marks_object = soup.find_all(name="td", class_="cell-middle center")
                    if not marks_object:
                        return None

                    marks_list = []

                    for mark_object in marks_object:
                        notification = False

                        if not mark_object:
                            continue

                        if not (
                            mark_string := mark_object.find_next(
                                name="strong"
                            ).get_text(strip=True)
                        ):
                            continue

                        try:
                            float(mark_string.replace("-", "").replace("+", ""))
                        except ValueError:
                            notification = True

                        assessment = mark_string

                        center_object = mark_object.find_next(
                            name="td", class_="center"
                        )
                        if not center_object:
                            continue

                        if not (
                            date_string := center_object.find_next(name="i").get_text(
                                strip=True
                            )
                        ):
                            continue

                        date = datetime.datetime.strptime(
                            date_string, "%d/%m/%Y"
                        ).date()

                        if not (
                            received_for := center_object.find_next(
                                name="div",
                                class_=True,
                            )
                            .find_next(name="i")
                            .get_text(strip=True)
                        ):
                            continue

                        if not (
                            subject_object := mark_object.find_next(
                                name="td", class_=False
                            )
                        ):
                            continue

                        subject_name = subject_object.find_next(name="strong").get_text(
                            strip=True
                        )

                        type_object = subject_object.find(name="span", class_="small")

                        notification_type = None
                        if type_object and notification:
                            notification_type = type_object.get_text(strip=True)

                        professor_name = subject_object.find_next(
                            name="i", class_="small"
                        ).get_text(strip=True)

                        description = (
                            subject_object.get_text(strip=True)
                            .replace(subject_name, "")
                            .replace(professor_name, "")
                        )

                        if notification and notification_type is not None:
                            description = description.replace(notification_type, "")

                        if description:
                            description = description[3:]

                        marks_list.append(
                            Mark(
                                subject_name=subject_name,
                                assessment=assessment,
                                description=description,
                                receiver_for=received_for,
                                date=date,
                                notification=notification,
                                notification_type=notification_type,
                            )
                        )

                    return list(reversed(marks_list))
                except Exception as ex:
                    logger.warning(
                        msg="Error when retrieving data from the diary!\n "
                        "This is a library error, file a bug report: https://github.com/Komo4ekoI/RighiDiaryAPI/issues"
                    )
                    raise ex
