from typing import List, Union
import aiohttp
import logging
import re
import json
import datetime

from . import __logger__
from . import _auth_functions

logger = logging.getLogger(__logger__ + "Schedule")


class Schedule:
    def __init__(
        self,
        lesson_name: str,
        date: datetime.date,
        start_time: datetime.time,
        end_time: datetime.time,
        day_name: str,
        professor_name: str,
        professor_surname: str,
    ):
        self.lesson_name = lesson_name.title() if isinstance(lesson_name, str) else lesson_name
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.day_name = day_name.lower() if isinstance(day_name, str) else day_name
        self.professor_name = professor_name.title() if isinstance(professor_name, str) else professor_name
        self.professor_surname = professor_surname.title() if isinstance(professor_surname, str) else professor_surname

    @property
    def full_professor_name(self) -> str:
        full_professor_name = f"{(self.professor_surname + ' ') if self.professor_surname is not None else ''}{self.professor_name if self.professor_name is not None else ''}"

        return full_professor_name

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


async def get_user_schedule(
    login: int,
    password: str,
    limit: int = None,
    daily: bool = False,
    PHPSESSID_cookie: str = None,
    messenger_cookie: str = None,
    current_key: str = None,
    user_id: int = None,
) -> Union[List[Schedule], None]:
    if not PHPSESSID_cookie or not messenger_cookie or not current_key or not user_id:
        response = await _auth_functions.fast_auth(password=password, login=login)

        if not response:
            logging.debug(msg="An error occurred when authorising to receive Schedule!")
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
                "stato_principale": "orario",
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
                return None
            else:
                try:
                    pattern = re.compile(r"JSON\.parse\('(.+?)'\);")
                    matches = pattern.search(await resp.text())
                    if matches:
                        try:
                            schedule_json = json.loads(matches.group(1))
                        except json.decoder.JSONDecodeError:
                            logger.debug(msg="Error in processing the received data!")
                            return None
                        try:
                            schedule_list_for_process = schedule_json[
                                f"{'elenco_ore_giornata' if daily else 'elenco_ore_totale'}"
                            ]
                        except KeyError:
                            logger.debug(msg="Error in processing the received data!")
                            return None

                        if not schedule_json:
                            logger.debug(msg="Missing schedule data!")
                            return None

                        schedule_list = []

                        position = 0
                        for entry in schedule_list_for_process:
                            professor_name = entry["nome_professore"]
                            professor_surname = entry["cognome_professore"]
                            lesson_name = entry["nome_materia_sito"]
                            date_string = entry["data_inizio_tradotta_iso"]
                            start_time_string = entry["ora_inizio_tradotta"]
                            end_time_string = entry["ora_fine_tradotta"]

                            day_name = entry["giorno_tradotto"]

                            date = datetime.datetime.strptime(
                                date_string, "%Y-%m-%d"
                            ).date()
                            start_time = datetime.datetime.strptime(
                                start_time_string, "%H:%M"
                            ).time()
                            end_time = datetime.datetime.strptime(
                                end_time_string, "%H:%M"
                            ).time()

                            item = Schedule(
                                lesson_name=lesson_name,
                                professor_name=professor_name,
                                professor_surname=professor_surname,
                                date=date,
                                start_time=start_time,
                                end_time=end_time,
                                day_name=day_name,
                            )

                            schedule_list.append(item)

                            position += 1
                            if limit is not None and position >= limit:
                                break

                        return schedule_list
                    else:
                        return None
                except Exception as ex:
                    logger.warning(
                        msg="Error when retrieving data from the diary!\n "
                            "This is a library error, file a bug report: https://github.com/Komo4ekoI/RighiDiaryAPI/issues"
                    )
                    raise ex
