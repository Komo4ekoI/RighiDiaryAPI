import datetime


def get_start_year() -> int:
    """
    Get the academic start year based on the current date.

    Returns:
        int: The academic start year.
    """
    today = datetime.date.today()

    start_year = (today.year - 1) if today.month < 9 else today.year

    return start_year
