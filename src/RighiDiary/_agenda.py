import aiohttp
import datetime
from bs4 import BeautifulSoup
from typing import Union, List
from logging import getLogger

from . import __logger__
from . import _auth_functions

logging = getLogger(__logger__ + ".Agenda")


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

    def __str__(self):
        attributes = ', '.join(f"{key}={value}" for key, value in vars(self).items())
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


def get_start_year() -> int:
    today = datetime.date.today()

    start_year = (today.year - 1) if today.month < 9 else today.year

    return start_year


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
            logging.debug(msg="An error occurred when authorising to receive Agenda!")
            return None

        PHPSESSID_cookie = response.PHPSESSID_cookie
        messenger_cookie = response.PHPSESSID_cookie
        current_key = response.current_key
        user_id = response.user_id

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
                logging.debug(
                    msg=f"Error on receipt of Agenda. Status: {response.status}"
                )
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

                        if (
                            int(short_italian_month[split_date[1]]) >= 8
                        ):
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
                            start_minutes = int(split_start_time[1])

                            start_time = datetime.time(
                                hour=start_hour, minute=start_minutes
                            )

                            end_time_string = time_text[5:]

                            split_end_time = end_time_string.split(":")
                            end_hour = int(split_end_time[0])
                            end_minutes = int(split_end_time[1])

                            end_time = datetime.time(hour=end_hour, minute=end_minutes)

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
                    logging.debug(msg="Error when retrieving data from the diary!")
                    raise ex
