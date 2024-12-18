import re
from typing import NamedTuple, Iterable

FIO_REGEXP = r"([А-ЯЁ][a-яё]+\s(?:[А-ЯЁ]\.){2})"
ROOM_NUMBER_REGEXP = r"(№\d+)"
SIMPLE_PARE_REGEXP = fr"I?I?(((?:[^_]*?\n)+?)(.*?){FIO_REGEXP}(.*?){ROOM_NUMBER_REGEXP})"
WEEK_DELIMITER_REGEXP = r"(?:_\s|_)+"
# WEEK_DELIMITER_REGEXP = r"_+"
HAS_WEEK_DELIMITER_REGEXP = fr'(?:I.*)?{WEEK_DELIMITER_REGEXP}(?:II.*)?'
PARES_BY_WEEKS_REGEXP = fr"(?:I{SIMPLE_PARE_REGEXP}\n)?{WEEK_DELIMITER_REGEXP}(?:\nII{SIMPLE_PARE_REGEXP})?"
FIRST_WEEK_ROOM_REGEXP = fr"I.*?{ROOM_NUMBER_REGEXP}"
SECOND_WEEK_ROOM_REGEXP = fr"II.*?{ROOM_NUMBER_REGEXP}"
ROOMS_BY_WEEKS_REGEXP = fr"((?:[^_]*?\n)*?)(.*?){FIO_REGEXP}(.*?)\n{FIRST_WEEK_ROOM_REGEXP}\s*?{SECOND_WEEK_ROOM_REGEXP}"
DIFFERENT_TEACHERS_REGEXP = fr"{SIMPLE_PARE_REGEXP}\n(.*?){FIO_REGEXP}(.*?){ROOM_NUMBER_REGEXP}"
THREE_DIFFERENT_TEACHERS_REGEXP = fr"{SIMPLE_PARE_REGEXP}\n(.*?){FIO_REGEXP}(.*?){ROOM_NUMBER_REGEXP}\n(.*?){FIO_REGEXP}(.*?){ROOM_NUMBER_REGEXP}"
HALF_GROUP_PARE = fr"{SIMPLE_PARE_REGEXP}\n{SIMPLE_PARE_REGEXP}"

class LessonData(NamedTuple):
    lesson_name: str
    teacher_post: str = None
    teacher_name: str = None
    room_number: int = None
    is_practice: bool = False
    is_even_week: bool = None

def cut(string: str):
    return ' '.join(string.strip().split())

def form_half_group_lesson(lesson: tuple, is_even_week: bool = None) -> LessonData:
    lesson = LessonData(
        lesson_name=cut(lesson[1]),
        teacher_post=cut(lesson[2]),
        teacher_name=cut(lesson[3]),
        room_number=int(cut(lesson[5])[1:]),
        is_practice=bool(cut(lesson[4])),
        is_even_week=is_even_week
    )
    return lesson

def form_week_changed_lessons(lessons: tuple) -> tuple[LessonData, LessonData]:
    if lessons[0]:
        lesson1 = LessonData(
            lesson_name=cut(lessons[1]),
            teacher_post=cut(lessons[2]),
            teacher_name=cut(lessons[3]),
            room_number=int(cut(lessons[5])[1:]),
            is_practice=bool(cut(lessons[4])),
            is_even_week=True
        )
    else:
        lesson1 = LessonData(
            lesson_name='Нет занятия',
            is_even_week=True
        )
    if lessons[6]:
        lesson2 = LessonData(
            lesson_name=cut(lessons[7]),
            teacher_post=cut(lessons[8]),
            teacher_name=cut(lessons[9]),
            room_number=int(cut(lessons[11])[1:]),
            is_practice=bool(cut(lessons[10])),
            is_even_week=False
        )
    else:
        lesson2 = LessonData(
            lesson_name='Нет занятия',
            is_even_week=False
        )
    return lesson1, lesson2

def form_different_teacher_lessons(lessons: tuple, is_even_week: bool = None) -> tuple[LessonData, LessonData]:
    lesson1 = LessonData(
        lesson_name=cut(lessons[1]),
        teacher_post=cut(lessons[2]),
        teacher_name=cut(lessons[3]),
        room_number=int(cut(lessons[5])[1:]),
        is_practice=bool(cut(lessons[4])),
        is_even_week=is_even_week
    )
    lesson2 = LessonData(
        lesson_name=cut(lessons[1]),
        teacher_post=cut(lessons[6]),
        teacher_name=cut(lessons[7]),
        room_number=int(cut(lessons[9])[1:]),
        is_practice=bool(cut(lessons[8])),
        is_even_week=is_even_week
    )
    return lesson1, lesson2

def form_three_teacher_lessons(lessons: tuple, is_even_week: bool = None) -> tuple[LessonData, LessonData, LessonData]:
    lesson1 = LessonData(
        lesson_name=cut(lessons[1]),
        teacher_post=cut(lessons[2]),
        teacher_name=cut(lessons[3]),
        room_number=int(cut(lessons[5])[1:]),
        is_practice=bool(cut(lessons[4])),
        is_even_week=is_even_week
    )
    lesson2 = LessonData(
        lesson_name=cut(lessons[1]),
        teacher_post=cut(lessons[6]),
        teacher_name=cut(lessons[7]),
        room_number=int(cut(lessons[9])[1:]),
        is_practice=bool(cut(lessons[8])),
        is_even_week=is_even_week
    )
    lesson3 = LessonData(
        lesson_name=cut(lessons[1]),
        teacher_post=cut(lessons[10]),
        teacher_name=cut(lessons[11]),
        room_number=int(cut(lessons[13])[1:]),
        is_practice=bool(cut(lessons[12])),
        is_even_week=is_even_week
    )
    return lesson1, lesson2, lesson3

def form_room_by_week_lessons(lessons: tuple) -> tuple[LessonData, LessonData]:
    lesson1 = LessonData(
        lesson_name=cut(lessons[0]),
        teacher_post=cut(lessons[1]),
        teacher_name=cut(lessons[2]),
        room_number=int(cut(lessons[4])[1:]),
        is_practice=bool(cut(lessons[3])),
        is_even_week=True
    )
    lesson2 = LessonData(
        lesson_name=cut(lessons[0]),
        teacher_post=cut(lessons[1]),
        teacher_name=cut(lessons[2]),
        room_number=int(cut(lessons[5])[1:]),
        is_practice=bool(cut(lessons[3])),
        is_even_week=False
    )
    return lesson1, lesson2

def form_simple_lesson(lessons: tuple, is_even_week: bool = None) -> LessonData:
    lesson1 = LessonData(
        lesson_name=cut(lessons[1]),
        teacher_post=cut(lessons[2]),
        teacher_name=cut(lessons[3]),
        room_number=int(cut(lessons[5])[1:]),
        is_practice=bool(cut(lessons[4])),
        is_even_week=is_even_week
    )
    return lesson1

def form_default(lesson_info: str, is_even_week: bool = None) -> LessonData:
    return LessonData(
        lesson_name=lesson_info,
        is_even_week=is_even_week
    )

def parse_lesson(lesson_info: str, is_even_week: bool=None) -> list[LessonData]:
    if lesson_info:
        lessons_data = []
        if re.fullmatch(ROOMS_BY_WEEKS_REGEXP, lesson_info):
            # print('Кабинеты по неделям')
            lessons = re.findall(ROOMS_BY_WEEKS_REGEXP, lesson_info)
            lesson1, lesson2 = form_room_by_week_lessons(lessons[0])
            lessons_data.append(lesson1)
            lessons_data.append(lesson2)
        elif re.fullmatch(HAS_WEEK_DELIMITER_REGEXP, lesson_info, re.DOTALL):
            # print('Разделитель по неделям')
            lesson1, lesson2 = re.split(WEEK_DELIMITER_REGEXP, lesson_info)
            lessons_data += parse_lesson(lesson1, is_even_week=True)
            lessons_data += parse_lesson(lesson2, is_even_week=False)
        elif re.match(THREE_DIFFERENT_TEACHERS_REGEXP, lesson_info):
            # print('Три препода')
            lessons = re.findall(THREE_DIFFERENT_TEACHERS_REGEXP, lesson_info)
            lesson1, lesson2, lesson3 = form_three_teacher_lessons(lessons[0], is_even_week=is_even_week)
            lessons_data.append(lesson1)
            lessons_data.append(lesson2)
            lessons_data.append(lesson3)
        elif re.match(DIFFERENT_TEACHERS_REGEXP, lesson_info):
            # print('Два препода')
            lessons = re.findall(DIFFERENT_TEACHERS_REGEXP, lesson_info)
            lesson1, lesson2 = form_different_teacher_lessons(lessons[0], is_even_week=is_even_week)
            lessons_data.append(lesson1)
            lessons_data.append(lesson2)
        elif re.match(HALF_GROUP_PARE, lesson_info):
            # print('Пара на пол группы')
            lesson1, lesson2 = re.findall(SIMPLE_PARE_REGEXP, lesson_info)
            lessons_data.append(form_half_group_lesson(lesson1, is_even_week=is_even_week))
            lessons_data.append(form_half_group_lesson(lesson2, is_even_week=is_even_week))
        # elif re.fullmatch(PARES_BY_WEEKS_REGEXP, lesson_info):
        #     lessons = re.findall(PARES_BY_WEEKS_REGEXP, lesson_info)
        #     lesson1, lesson2 = form_week_changed_lessons(lessons[0])
        #     lessons_data.append(lesson1)
        #     lessons_data.append(lesson2)
        elif re.match(SIMPLE_PARE_REGEXP, lesson_info):
            # print('Просто пара')
            lessons = re.findall(SIMPLE_PARE_REGEXP, lesson_info)
            lessons_data.append(form_simple_lesson(lessons[0], is_even_week=is_even_week))
        else:
            # print('Что-то ещё')
            lessons_data.append(form_default(lesson_info, is_even_week=is_even_week))
        return lessons_data
    else:
        # print('Нет пары')
        return [LessonData(lesson_name='Нет занятия', is_even_week=is_even_week)]


if __name__ == '__main__':
    lesson = """I 1/2 Теория принятия решений
Проф. Иванова И.В. пр. №831
1/2 Информационные технологии
Проф. Бригаднов И.А. пр. №336
______________________"""

    lesson = parse_lesson(lesson_info=lesson)
    print(lesson)