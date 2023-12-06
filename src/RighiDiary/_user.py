from typing import Union, List

from ._baseprofile import BaseProfile
from ._agenda import Agenda, get_user_agenda
from ._homework import Homework, get_user_homework


class User(BaseProfile):
    """
    User - base class, stores all data about the user. Allows you to update data via MastercomAPI
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
        homework: Union[List[Homework], None]
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

    @property
    def full_name(self) -> Union[str, None]:
        """
        Takes the first and last name of the user and returns the full name of the user.\n
        Example:\n
        Name - Vadym\n
        Last name - Teliatnyk\n
        Return - Teliatnyk Vadym
        :return: str | None
        """
        name = self.name
        surname = self.surname

        full_name = f"{(surname + ' ') if surname is not None else ''}{name if name is not None else ''}"

        return full_name if full_name else None

    async def update_user_agenda(self) -> List[Agenda]:
        new_agenda = await get_user_agenda(
            login=super().login, password=super().password
        )
        self.agenda = new_agenda

        return new_agenda

    async def update_user_homework(self) -> List[Homework]:
        new_homework = await get_user_homework(
            login=super().login, password=super().password
        )
        self.homework = new_homework

        return new_homework

    def __str__(self):
        attributes = ", ".join(f"{key}={value}" for key, value in vars(self).items())
        return f"{self.__class__.__name__}({attributes})"
