weekdays = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница']


def get_week_day_number(week_day_name: str) -> int:
    return weekdays.index(week_day_name.lower()) + 1


def get_week_day_name(week_day_number: int) -> str:
    return weekdays[week_day_number - 1]
