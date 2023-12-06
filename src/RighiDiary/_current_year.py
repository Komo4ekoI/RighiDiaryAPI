import datetime


def get_start_year() -> int:
    today = datetime.date.today()

    start_year = (today.year - 1) if today.month < 9 else today.year

    return start_year
