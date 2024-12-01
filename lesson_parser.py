import re

from database.model import Lesson


def parse_lesson(lesson_info: str) -> list[Lesson]:
    lessons_info = []
    if not lessons:
        return None
    else:
        lessons = re.split(r'\n_+\n', lessons)
        for lesson in lessons:
            lessons_info += self.parse_lesson_info(lesson)
        return lessons_info


    def parse_lesson_info(self, lesson) -> list[dict]:
        teachers = re.findall(r'[А-ЯЁ][a-яё]+\s[А-ЯЁ]\.{2}', lesson)
