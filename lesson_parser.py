import re
from typing import NamedTuple, Iterable

FIO_REGEXP = r"([А-ЯЁ][a-яё]+\s(?:[А-ЯЁ]\.){2})"
ROOM_NUMBER_REGEXP = r"(№\d+)"
SIMPLE_PARE_REGEXP = fr"(((?:[^_]*?\n)+?)(.*?){FIO_REGEXP}(.*?){ROOM_NUMBER_REGEXP})"
WEEK_DELIMITER_REGEXP = r"_+"
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
    is_practice: bool = None
    is_even_week: bool = None

def cut(string: str):
    return ' '.join(string.strip().split())

def form_half_group_lesson(lesson: tuple) -> LessonData:
    lesson = LessonData(
        lesson_name=cut(lesson[1]),
        teacher_post=cut(lesson[2]),
        teacher_name=cut(lesson[3]),
        room_number=int(cut(lesson[5])[1:]),
        is_practice=bool(cut(lesson[4])),
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
            lesson_name='Нет занятия'
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
            lesson_name='Нет занятия'
        )
    return lesson1, lesson2

def form_different_teacher_lessons(lessons: tuple) -> tuple[LessonData, LessonData]:
    lesson1 = LessonData(
        lesson_name=cut(lessons[1]),
        teacher_post=cut(lessons[2]),
        teacher_name=cut(lessons[3]),
        room_number=int(cut(lessons[5])[1:]),
        is_practice=bool(cut(lessons[4]))
    )
    lesson2 = LessonData(
        lesson_name=cut(lessons[1]),
        teacher_post=cut(lessons[6]),
        teacher_name=cut(lessons[7]),
        room_number=int(cut(lessons[9])[1:]),
        is_practice=bool(cut(lessons[8]))
    )
    return lesson1, lesson2

def form_three_teacher_lessons(lessons: tuple) -> tuple[LessonData, LessonData, LessonData]:
    lesson1 = LessonData(
        lesson_name=cut(lessons[1]),
        teacher_post=cut(lessons[2]),
        teacher_name=cut(lessons[3]),
        room_number=int(cut(lessons[5])[1:]),
        is_practice=bool(cut(lessons[4]))
    )
    lesson2 = LessonData(
        lesson_name=cut(lessons[1]),
        teacher_post=cut(lessons[6]),
        teacher_name=cut(lessons[7]),
        room_number=int(cut(lessons[9])[1:]),
        is_practice=bool(cut(lessons[8]))
    )
    lesson3 = LessonData(
        lesson_name=cut(lessons[1]),
        teacher_post=cut(lessons[10]),
        teacher_name=cut(lessons[11]),
        room_number=int(cut(lessons[13])[1:]),
        is_practice=bool(cut(lessons[12]))
    )
    return lesson1, lesson2, lesson3

def form_room_by_week_lessons(lessons: tuple) -> tuple[LessonData, LessonData]:
    print(lessons)
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

def form_simple_lesson(lessons: tuple) -> LessonData:
    lesson1 = LessonData(
        lesson_name=cut(lessons[1]),
        teacher_post=cut(lessons[2]),
        teacher_name=cut(lessons[3]),
        room_number=int(cut(lessons[5])[1:]),
        is_practice=bool(cut(lessons[4]))
    )
    return lesson1

def form_default(lesson_info: str) -> LessonData:
    return LessonData(
        lesson_name=lesson_info
    )

def parse_lesson(lesson_info: str) -> list[LessonData]:
    if lesson_info:
        lessons_data = []
        if re.fullmatch(THREE_DIFFERENT_TEACHERS_REGEXP, lesson_info):
            lessons = re.findall(THREE_DIFFERENT_TEACHERS_REGEXP, lesson_info)
            lesson1, lesson2, lesson3 = form_three_teacher_lessons(lessons[0])
            lessons_data.append(lesson1)
            lessons_data.append(lesson2)
            lessons_data.append(lesson3)
        if re.fullmatch(DIFFERENT_TEACHERS_REGEXP, lesson_info):
            lessons = re.findall(DIFFERENT_TEACHERS_REGEXP, lesson_info)
            lesson1, lesson2 = form_different_teacher_lessons(lessons[0])
            lessons_data.append(lesson1)
            lessons_data.append(lesson2)
        elif re.fullmatch(ROOMS_BY_WEEKS_REGEXP, lesson_info):
            lessons = re.findall(ROOMS_BY_WEEKS_REGEXP, lesson_info)
            lesson1, lesson2 = form_room_by_week_lessons(lessons[0])
            lessons_data.append(lesson1)
            lessons_data.append(lesson2)
        elif re.fullmatch(HALF_GROUP_PARE, lesson_info):
            lesson1, lesson2 = re.findall(SIMPLE_PARE_REGEXP, lesson_info)
            lessons_data.append(form_half_group_lesson(lesson1))
            lessons_data.append(form_half_group_lesson(lesson2))
        elif re.fullmatch(PARES_BY_WEEKS_REGEXP, lesson_info):
            lessons = re.findall(PARES_BY_WEEKS_REGEXP, lesson_info)
            lesson1, lesson2 = form_week_changed_lessons(lessons[0])
            lessons_data.append(lesson1)
            lessons_data.append(lesson2)
        elif re.fullmatch(SIMPLE_PARE_REGEXP, lesson_info):
            lessons = re.findall(SIMPLE_PARE_REGEXP, lesson_info)
            lessons_data.append(form_simple_lesson(lessons[0]))
        else:
            lessons_data.append(form_default(lesson_info))
        return lessons_data
    else:
        return [LessonData(lesson_name='Нет занятия')]


if __name__ == '__main__':
    lesson = """____________________\nII 1/2 Физика Земли\nДоц. Егорова Ю.С. пр. № Горный музей"""
    print(THREE_DIFFERENT_TEACHERS_REGEXP)
    lesson = parse_lesson(lesson_info=lesson)
    print(lesson)