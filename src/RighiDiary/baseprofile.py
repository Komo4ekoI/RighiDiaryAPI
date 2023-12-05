class BaseProfile:
    def __init__(self, login: int, password: str):
        self._login = login
        self._password = password

    @property
    def login(self) -> int:
        return self._login

    @property
    def password(self) -> str:
        return self._password
