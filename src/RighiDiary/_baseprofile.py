class BaseProfile:
    """
    A base class representing a user profile with login and password.

    Attributes:
        login (int): Login for mastercom account. Usually consists of 6 digits.
        password (str): Password for the mastercom account.
    """

    def __init__(self, login: int, password: str):
        self.login = login
        self.password = password
