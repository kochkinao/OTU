import os

import pandas

from database.model import Lesson
from settings import SOURCE_DIR
import sqlalchemy
from dotenv import load_dotenv
from timetable_parser_v2 import TimetablePDFParser
from lesson_parser import parse_lesson


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


def parse_timetable(timetable_data: pandas.DataFrame):
    for i, row in timetable_data.iterrows():
        if row['lesson']:
            try:
                lessons = parse_lesson(lesson_info=row['lesson'])
            except Exception as ex:
                print(ex)


def parse_timetables(timetable_dir=TIMETABLE_DIR):
    parser = TimetablePDFParser()  # Устанавливаем парсер
    files = list_files_in_directory(timetable_dir)  # Находим все PDF-файлы
    for file in files:
        df = parser.parse_pdf(filepath=file)  # Парсим их в pandas.DataFrame
        parse_timetable(df)


if __name__ == '__main__':
    # conn = psycopg2.connect("dbname='shedule' user='postgres' host='localhost' port='7546' password='root'")
    # conn.cursor().execute('INSERT INTO class VALUES (%s, %s, %s, %s, %s)',
    #                             ['Понеденьник', '10:35', '12:05', 'ИАС-22-1', 'yaslknaslflknadsv'])
    # conn.commit()
    parse_timetables(SOURCE_DIR)
