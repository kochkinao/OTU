from datetime import datetime
import os
from traceback import print_exception

import pandas
from database.db_manager import DbManager
from database.model import Group, Teacher, ClassSchedule, Lesson
from lesson_parser import parse_lesson
from settings import SOURCE_DIR, DB_URL
from timetable_parser_v2 import TimetablePDFParser
from weekdays import get_week_day_number

TIMETABLE_DIR = 'timetables'


def list_files_in_directory(directory_path):
    """Перебирать все PDF-файлы в папке"""
    file_paths = []
    # Получаем список всех файлов и папок в указанной папке
    for file_name in os.listdir(directory_path):
        # Строим полный путь к файлу
        file_path = os.path.join(directory_path, file_name)
        # Проверяем, является ли это PDF-файлом
        if os.path.isfile(file_path) and file_name.endswith('.pdf'):
            file_paths.append(file_path)
    return file_paths


def load_groups(db_manager: DbManager, group_names: list[str], year: int):
    for group_name in group_names:
        if group := db_manager.find_group_by_name(group_name):
            group.course = year
        else:
            group = Group(name=group_name, course=year)
        db_manager.save(group)

def check_teacher(db_manager: DbManager, teacher_name: str, teacher_post: str):
    if teacher := db_manager.find_teacher_by_name(teacher_name):
        if teacher.post != teacher_post:
            teacher.post = teacher_post
            db_manager.save(teacher)
    elif teacher_name:
        teacher = Teacher(full_name=teacher_name, post=teacher_post)
        db_manager.save(teacher)
    return teacher


def parse_timetable(db_manager: DbManager, timetable_data: pandas.DataFrame):
    for i, row in timetable_data.iterrows():
        if row['lesson']:
            try:
                lessons = parse_lesson(lesson_info=row['lesson'])
                for lesson in lessons:
                    teacher = check_teacher(db_manager, lesson.teacher_name, lesson.teacher_post)
                    group = db_manager.find_group_by_name(row['group'])
                    pair = db_manager.find_pair_by_start_time(row['start_time'])
                    if lesson.is_even_week is not None:
                        new_lesson = Lesson(
                            day_of_week=get_week_day_number(row['week_day']),
                            room_number=lesson.room_number,
                            subject=lesson.lesson_name,
                            is_even_week=lesson.is_even_week,
                            is_practice=lesson.is_practice,
                            pair=pair,
                            group=group,
                            teacher=teacher
                        )
                        db_manager.save(new_lesson)
                    else:
                        new_lesson = Lesson(
                            day_of_week=get_week_day_number(row['week_day']),
                            room_number=lesson.room_number,
                            subject=lesson.lesson_name,
                            is_even_week=True,
                            is_practice=lesson.is_practice,
                            pair=pair,
                            group=group,
                            teacher=teacher
                        )
                        db_manager.save(new_lesson)
                        new_lesson = Lesson(
                            day_of_week=get_week_day_number(row['week_day']),
                            room_number=lesson.room_number,
                            subject=lesson.lesson_name,
                            is_even_week=False,
                            is_practice=lesson.is_practice,
                            pair=pair,
                            group=group,
                            teacher=teacher
                        )
                        db_manager.save(new_lesson)
            except Exception as ex:
                print('Ошибка во время парсинга строки:')
                print(row['lesson'])
                print_exception(ex)


def load_times(db_manager, pair_times):
    times = []
    for new_time in pair_times:
        start_time, end_time = new_time.split('-')
        start_time = datetime.strptime(start_time, '%H:%M').time()
        end_time = datetime.strptime(end_time, '%H:%M').time()
        times.append((start_time, end_time))
    times.sort(key=lambda t: t[0])
    for i, new_time in enumerate(times):
        if not db_manager.find_pair_by_number(i+1):
            pair = ClassSchedule(pair_number=i+1, start_time=new_time[0], end_time=new_time[1])
            db_manager.save(pair)


def parse_timetables(db_manager: DbManager, timetable_dir=TIMETABLE_DIR):
    db_manager.remove_all_lessons()
    parser = TimetablePDFParser()  # Устанавливаем парсер
    files = list_files_in_directory(timetable_dir)  # Находим все PDF-файлы
    for file in files:
        print(file)
        df, group_names, pair_times = parser.parse_pdf(filepath=file)  # Парсим их в pandas.DataFrame
        load_times(db_manager, pair_times)
        load_groups(db_manager, group_names, year=int(file.split('\\')[1][0]))
        parse_timetable(db_manager, df)


if __name__ == '__main__':
    parse_timetables(DbManager(DB_URL), SOURCE_DIR)
