import aiohttp
import datetime
from bs4 import BeautifulSoup
from typing import Union, List
import logging

from ._current_year import get_start_year
from . import __logger__
from . import _auth_functions

logger = logging.getLogger(__logger__ + ".Agenda")


class Agenda:
    def __init__(
        self,
        name: Union[str, None],
        description: Union[str, None],
        date: datetime.date,
        start_time: datetime.time,
        end_time: datetime.time,
        professor_name: str,
    ):
        self.name = name if name else None
        self.description = description if description else None
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.professor_name = professor_name

    @property
    def duration(self) -> datetime.time:
        seconds_start = self.start_time.hour * 3600 + self.start_time.minute * 60
        seconds_end = self.end_time.hour * 3600 + self.end_time.minute * 60

        difference_seconds = abs(seconds_end - seconds_start)

        hours, remainder = divmod(difference_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        return datetime.time(hours, minutes, seconds)

    def __str__(self):
        attributes = ", ".join(f"{key}={value}" for key, value in vars(self).items())
        return f"{self.__class__.__name__}({attributes})"


short_italian_month = {
    "gen": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "mag": 5,
    "giu": 6,
    "lug": 7,
    "ago": 8,
    "set": 9,
    "ott": 10,
    "nov": 11,
    "dic": 12,
}


async def get_user_agenda(
    login: int,
    password: str,
    PHPSESSID_cookie: str = None,
    messenger_cookie: str = None,
    current_key: str = None,
    user_id: int = None,
) -> Union[List[Agenda], None]:
    if not PHPSESSID_cookie or not messenger_cookie or not current_key or not user_id:
        response = await _auth_functions.fast_auth(password=password, login=login)

        if not response:
            logger.debug(msg="An error occurred when authorising to receive Agenda!")
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
                "stato_principale": "agenda",
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
                agenda_list = []
                try:
                    soup = BeautifulSoup(await response.text(), features="html.parser")
                    results = soup.find_all(
                        name="tr", class_="border-bottom border-gray"
                    )
                    for result in results:
                        if not result:
                            continue

                        date_object = result.find_next(name="td", class_="center").find(
                            name="strong", class_=False
                        )
                        split_date = (
                            date_object.get_text(strip=True)
                            .replace(" ", "")
                            .replace("\n", " ")
                            .split(" ")
                        )

                        day = int(split_date[0])
                        month = int(short_italian_month[split_date[1]])

                        current_school_start_year = get_start_year()

                        if int(short_italian_month[split_date[1]]) >= 8:
                            year = current_school_start_year
                        else:
                            year = current_school_start_year + 1

                        date = datetime.date(year=year, month=month, day=day)

                        data_objects = result.find_all(
                            name="div",
                            class_="padding-small border-left-2 margin-bottom border-green",
                        )

                        for data_object in data_objects:
                            if not data_object:
                                continue

                            time_text = data_object.find_next(
                                name="div", class_="right right-align"
                            ).get_text(strip=True)

                            start_time_string = time_text[:5]

                            split_start_time = start_time_string.split(":")
                            start_hour = int(split_start_time[0])
                            start_minute = int(split_start_time[1])

                            start_time = datetime.time(
                                hour=start_hour, minute=start_minute
                            )

                            end_time_string = time_text[5:]

                            split_end_time = end_time_string.split(":")
                            end_hour = int(split_end_time[0])
                            end_minute = int(split_end_time[1])

                            end_time = datetime.time(hour=end_hour, minute=end_minute)

                            name = data_object.find_next(name="strong").get_text(
                                strip=True
                            )

                            professor_name = (
                                data_object.find_next(
                                    name="i", class_="text-gray small"
                                )
                                .get_text(strip=True)
                                .replace("(", "")
                                .replace(")", "")
                            )

                            description = (
                                data_object.get_text(strip=True)
                                .replace("(" + professor_name + ")", "")
                                .replace(start_time_string, "")
                                .replace(end_time_string, "")
                                .replace(name, "")
                            )

                            agenda_list.append(
                                Agenda(
                                    name=name,
                                    description=description,
                                    date=date,
                                    start_time=start_time,
                                    end_time=end_time,
                                    professor_name=professor_name,
                                )
                            )
                    return list(reversed(agenda_list))
                except Exception as ex:
                    logger.debug(
                        msg="Error when retrieving data from the diary!\n "
                            "This is a library error, file a bug report: https://github.com/Komo4ekoI/RighiDiaryAPI/issues"
                    )
                    raise ex
