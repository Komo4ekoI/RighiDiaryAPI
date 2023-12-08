from typing import Union, List

from ._baseprofile import BaseProfile
from ._agenda import Agenda, get_user_agenda
from ._homework import Homework, get_user_homework
from ._schedule import Schedule, get_user_schedule
from ._marks import Mark, get_user_marks


class User(BaseProfile):
    """
    User - base class, stores all data about the user. Allows you to update data via MastercomAPI.

    Attributes:
        login (int): Login for mastercom account. Usually consists of 6 digits.
        password (str): Password for the mastercom account.
        name (str): Name of the user.
        surname (str): Surname of the user.
        mastercom_id (str, optional): User ID in mastercom database.
        current_key (str, optional): KEY of the authorised session in the mastercom system.
        classes (str): Class to which the student belongs at the lyceum.
        phone (str, optional): Phone number of the student.
        email (str, optional): Email address of the student.
        agenda (list of :class:`RighiDiary.Agenda`, optional): User Agenda. Can be None if an error occurred while receiving the data.
        homework (list of :class:`RighiDiary.Homework`, optional): User Homework. Can be None if an error occurred while receiving the data.
        schedule (list of :class:`RighiDiary.Schedule`, optional): User Schedule. Can be None if an error occurred while receiving the data.
        marks (list of :class:`RighiDiary.Mark`, optional): User Marks. Can be None if an error occurred while receiving the data.
    """

    def __init__(
        self,
        login: int,
        password: str,
        name: Union[str, None],
        surname: Union[str, None],
        mastercom_id: Union[str, None],
        current_key: Union[str, None],
        classes: str,
        phone: Union[str, None],
        email: Union[str, None],
        agenda: Union[List[Agenda], None],
        homework: Union[List[Homework], None],
        schedule: Union[List[Schedule], None],
        marks: Union[List[Mark], None],
    ):
        self.surname = surname
        self.name = name
        self.current_key = current_key
        self.mastercom_id = mastercom_id
        self.classes = classes
        self.phone = phone
        self.email = email
        super().__init__(login=login, password=password)
        self.agenda = agenda
        self.homework = homework
        self.schedule = schedule
        self.marks = marks

    @property
    def full_name(self) -> Union[str, None]:
        """
        Takes the first and last name of the user and returns the full name of the user.\n
        Example:\n
            Name - Vadym\n
            Last name - Teliatnyk\n
            Result - Teliatnyk Vadym
        :return: Full name of the authorized user.
        """
        name = self.name
        surname = self.surname

        full_name = f"{(surname + ' ') if surname is not None else ''}{name if name is not None else ''}"

        return full_name if full_name else None

    async def update_user_agenda(self) -> Union[List[Agenda], None]:
        """
        Updates the user Agenda using login and password. This replaces the current data in the class with the new data.
        :return: Returns the RighiDiary.Agenda class if it succeeded in updating the data, otherwise returns None.
        """
        new_agenda = await get_user_agenda(
            login=super().login, password=super().password
        )
        self.agenda = new_agenda

        return new_agenda

    async def update_user_homework(self) -> Union[List[Homework], None]:
        """
        Updates the user Homework using login and password. This replaces the current data in the class with the new data.
        :return: Returns the RighiDiary.Homework class if it succeeded in updating the data, otherwise returns None.
        """
        new_homework = await get_user_homework(
            login=super().login, password=super().password
        )
        self.homework = new_homework

        return new_homework

    async def update_user_schedule(
        self, limit: int = None, daily: bool = None
    ) -> Union[List[Schedule], None]:
        """
        Updates the user Schedule using login and password. This replaces the current data in the class with the new data.
        :param limit: The limit of data to be obtained from the diary. Important, 1 data type is not 1 day of schedule, it is 1 lesson.
        :param daily: Switches the data acquisition mode. If True, it will search for data for the current day, otherwise it will return a list of all available data.
        :return: Returns the RighiDiary.Schedule class if it succeeded in updating the data, otherwise returns None.
        """
        new_schedule = await get_user_schedule(
            login=super().login, password=super().password, limit=limit, daily=daily
        )
        self.schedule = new_schedule

        return new_schedule

    async def update_user_marks(self) -> Union[List[Schedule], None]:
        """
        Updates the user Marks using login and password. This replaces the current data in the class with the new data.
        :return: Returns the RighiDiary.Marks class if it succeeded in updating the data, otherwise returns None.
        """
        new_marks = await get_user_marks(
            login=super().login,
            password=super().password,
        )
        self.marks = new_marks

        return new_marks

    def __str__(self):
        attributes = ", ".join(f"{key}={value}" for key, value in vars(self).items())
        return f"{self.__class__.__name__}({attributes})"
