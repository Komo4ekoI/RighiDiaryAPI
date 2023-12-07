import logging
from typing import List, Union
import datetime
import aiohttp
from bs4 import PageElement, BeautifulSoup
import re

from ._current_year import get_start_year
from . import __logger__
from . import _auth_functions

logger = logging.getLogger(__logger__ + "Homework")


class Homework:
    def __init__(
        self,
        subject_name: str,
        text: str,
        date: datetime.date,
        time: datetime.time,
        professor_name: str,
    ):
        self.subject_name = subject_name
        self.text = text if text else None
        self.date = date
        self.time = time
        self.professor_name = professor_name

    def __str__(self):
        attributes = ", ".join(f"{key}={value}" for key, value in vars(self).items())
        return f"{self.__class__.__name__}({attributes})"


italian_month = {
    "gennaio": 1,
    "febbraio": 2,
    "marzo": 3,
    "aprile": 4,
    "maggio": 5,
    "giugno": 6,
    "luglio": 7,
    "agosto": 8,
    "settembre": 9,
    "ottobre": 10,
    "novembre": 11,
    "dicembre": 12,
}


async def get_exercises_data(
    result: PageElement, current_date: datetime.date, homework_list: List[Homework]
) -> List[Homework]:
    subjects = result.find_all(name="td", class_="border-left border-gray padding-8")

    for subject in subjects:
        subject_name_object = subject.find_next(name="strong")
        subject_name = subject_name_object.text
        homework_objects = subject.find_all(
            name="div",
            class_="padding-small border-left-2 margin-bottom-small border-amber",
        )

        for homework_object in homework_objects:
            homework_text = homework_object.get_text(strip=True)
            if "Da fare" in homework_text:
                text = homework_text.split("Da fare")[0].replace("\n", " ")
            else:
                text = homework_text.split("Fatto")[0].replace("\n", " ")
            if not text:
                continue
            professor_info_object = homework_object.find_next(
                name="i", class_="text-gray small"
            )
            professor_name = (
                professor_info_object.text.replace("(", "")
                .replace(")", "")
                .split(" - ")[1]
            )

            lesson_time = (
                professor_info_object.text.replace("(", "")
                .replace(")", "")
                .split(" - ")[0]
            )

            if not lesson_time:
                continue

            split_time = lesson_time.split(":")

            hour = int(split_time[0])
            minute = int(split_time[1])

            time = datetime.time(hour=hour, minute=minute)

            homework_list.append(
                Homework(
                    subject_name=subject_name,
                    text=text,
                    date=current_date,
                    time=time,
                    professor_name=professor_name,
                )
            )

    return homework_list


async def get_user_homework(
    login: int,
    password: str,
    PHPSESSID_cookie: str = None,
    messenger_cookie: str = None,
    current_key: str = None,
    user_id: int = None,
) -> Union[List[Homework], None]:
    if not PHPSESSID_cookie or not messenger_cookie or not current_key or not user_id:
        response = await _auth_functions.fast_auth(password=password, login=login)

        if not response:
            logger.debug(msg="An error occurred when authorising to receive Homework!")
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
                "stato_principale": "argomenti-compiti",
                "stato_secondario": "",
                "permission": "",
                "operazione": "",
                "current_user": str(user_id),
                "current_key": current_key,
                "from_app": "",
                "header": "SI",
            },
        ) as response:
            if response.status != 200:
                logger.debug(
                    msg=f"Error on receipt of Agenda. Status: {response.status}"
                )
                return None
            else:
                try:
                    soup = BeautifulSoup(await response.text(), features="html.parser")
                    results = soup.find_all(
                        name="tr", class_="border-bottom border-gray"
                    )

                    subjects_list = []
                    current_date = None

                    for result in results:
                        if not result:
                            continue

                        try:
                            date_strong = result.find_next(name="strong")

                            cleaned_date = re.sub(
                                r"(\d)([a-zA-Z])",
                                r"\1 \2",
                                date_strong.text.replace(" ", "")
                                .replace("\n", "")
                                .replace("\t", ""),
                            )

                            if cleaned_date is None:
                                continue

                            split_date = cleaned_date.split(" ")

                            if len(split_date) < 2:
                                raise TypeError

                            try:
                                day = int(split_date[0])
                                month = italian_month[split_date[1]]
                            except:
                                raise TypeError

                            if month >= 8:
                                year = get_start_year()
                            else:
                                year = get_start_year() + 1

                            if not day or not month:
                                raise TypeError

                            current_date = datetime.date(year=year, month=month, day=day)

                            subjects_list = await get_exercises_data(
                                result=result,
                                current_date=current_date,
                                homework_list=subjects_list,
                            )

                        except TypeError:
                            subjects_list = await get_exercises_data(
                                result=result,
                                current_date=current_date,
                                homework_list=subjects_list,
                            )
                    return list(reversed(subjects_list))
                except Exception as ex:
                    logger.debug(msg="Error when retrieving data from the diary!")
                    raise ex
