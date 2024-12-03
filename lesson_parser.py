import re
from typing import NamedTuple

FIO_REGEXP = r"([А-ЯЁ][a-яё]+\s(?:[А-ЯЁ]\.){2})"
ROOM_NUMBER_REGEXP = r"(№\d+)"
SIMPLE_PARE_REGEXP = fr"(((?:.*?\n)*?)(.*?){FIO_REGEXP}(.*?){ROOM_NUMBER_REGEXP})"
WEEK_DELIMITER_REGEXP = r"_+"
PARES_BY_WEEKS_REGEXP = fr"(?:I{SIMPLE_PARE_REGEXP}\n)?{WEEK_DELIMITER_REGEXP}(?:\nII{SIMPLE_PARE_REGEXP})?"
FIRST_WEEK_ROOM_REGEXP = fr"I.*?{ROOM_NUMBER_REGEXP}"
SECOND_WEEK_ROOM_REGEXP = fr"II.*?{ROOM_NUMBER_REGEXP}"
ROOMS_BY_WEEKS_REGEXP = fr"(((?:.*?\n)*?)(.*?){FIO_REGEXP}(.*?)\n{FIRST_WEEK_ROOM_REGEXP}\s*?{SECOND_WEEK_ROOM_REGEXP}"
DIFFERENT_TEACHERS_REGEXP = fr"{SIMPLE_PARE_REGEXP}\n(.*?){FIO_REGEXP}(.*?){ROOM_NUMBER_REGEXP}"
HALF_GROUP_PARE = fr"{SIMPLE_PARE_REGEXP}\n{SIMPLE_PARE_REGEXP}"

class LessonData(NamedTuple):
    lesson_name: str
    teacher_post: str = None
    teacher_name: str = None
    room_number: int = None
    is_practice: bool = None
    is_even_week: bool = None

def cut(string: str):
    return ' '.join(string.strip().split())

def form_lesson(lesson: tuple) -> LessonData:
    lesson = LessonData(
        lesson_name=cut(lesson[1]),
        teacher_post=cut(lesson[2]),
        teacher_name=cut(lesson[3]),
        room_number=int(cut(lesson[5])[1:]),
        is_practice=bool(cut(lesson[4])),
        is_even_week=True
    )
    return lesson

def parse_lesson(lesson_info: str) -> tuple[LessonData, LessonData]:
    if lesson_info:
        if re.match(HALF_GROUP_PARE, lesson_info):
            lesson1, lesson2 = re.findall(SIMPLE_PARE_REGEXP, lesson_info)
            print(form_lesson(lesson1))
            print(lesson2)
    else:
        return lesson


if __name__ == '__main__':
    lesson = """ч/н 1/2 Архитектура вычислительных систем
(выбранные дисциплины)
Доц. Соколов О.Б. пр. №314
ч/н 1/2 Администрирование в
информационных системах
Доц. Ямпольский В.Л. пр. №313"""
    print(HALF_GROUP_PARE)
    parse_lesson(lesson_info=lesson)
