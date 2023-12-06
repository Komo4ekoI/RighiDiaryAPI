from typing import Union, List
import asyncio

from ._baseprofile import BaseProfile
from ._agenda import Agenda, get_user_agenda


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
    ):
        super().__init__(login=login, password=password)
        self.current_key = current_key
        self.mastercom_id = mastercom_id
        self._surname = surname
        self._name = name
        self.classes = classes
        self.phone = phone
        self.email = email
        self.agenda = agenda

    @property
    def name(self) -> Union[str, None]:
        return self._name if self._name else None

    @property
    def surname(self) -> Union[str, None]:
        return self._name if self._name else None

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
        new_agenda = await get_user_agenda(login=super().login, password=super().password)
        self.agenda = new_agenda

        return new_agenda

