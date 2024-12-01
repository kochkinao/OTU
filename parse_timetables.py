import os
import psycopg2
import sqlalchemy
from dotenv import load_dotenv
from timetable_parser import TimetablePDFParser


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


def parse_timetables(timetable_dir=TIMETABLE_DIR):
    parser = TimetablePDFParser()  # Устанавливаем парсер
    files = list_files_in_directory(timetable_dir)  # Находим все PDF-файлы
    df = parser.parse_all_pdfs(filepaths=files)  # Парсим их в pandas.DataFrame
    conn = sqlalchemy.create_engine(os.getenv("DB_URL")).connect()

    df.to_sql(name='class', con=conn, if_exists='append', index=False)


if __name__ == '__main__':
    # conn = psycopg2.connect("dbname='shedule' user='postgres' host='localhost' port='7546' password='root'")
    # conn.cursor().execute('INSERT INTO class VALUES (%s, %s, %s, %s, %s)',
    #                             ['Понеденьник', '10:35', '12:05', 'ИАС-22-1', 'yaslknaslflknadsv'])
    # conn.commit()
    load_dotenv()
    parse_timetables(TIMETABLE_DIR)
