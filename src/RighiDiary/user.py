from src.RighiDiary.baseprofile import BaseProfile
from typing import Union


class User(BaseProfile):
    """
    User - base class, stores all data about the user. Allows you to update data via MastercomAPI
    """
    def __init__(
        self,
        login: int,
        password: str,
        name: str,
        surname: str,
        mastercom_id: int,
        current_key: str,
    ):
        super().__init__(login=login, password=password)
        self._current_key = current_key
        self._mastercom_id = mastercom_id
        self._surname = surname
        self._name = name

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

        full_name = f"{surname + ' ' if surname is not None else ''}{name if name is not None else ''}"

        return full_name if full_name else None

