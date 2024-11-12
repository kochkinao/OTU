import os

from timetable_parser import TimetablePDFParser

TIMETABLE_DIR = 'timetables'
OUT_FILE = 'schedule.csv'


def list_files_in_directory(directory_path):
    """Перебират все PDF-файлы в папке"""
    file_paths = []
    # Получаем список всех файлов и папок в указанной папке
    for file_name in os.listdir(directory_path):
        # Строим полный путь к файлу
        file_path = os.path.join(directory_path, file_name)
        # Проверяем, является ли это PDF-файлом
        if os.path.isfile(file_path) and file_name.endswith('.pdf'):
            file_paths.append(file_path)
    return file_paths


def parse_timetables(timetable_dir, out_file):
    parser = TimetablePDFParser()  # Устанавливаем парсер
    files = list_files_in_directory(timetable_dir)  # Находим все PDF-файлы
    df = parser.parse_all_pdfs(filepaths=files)  # Парсим их в pandas.DataFrame
    df.to_csv(out_file, index=False)  # Экспортируем в CSV


if __name__ == '__main__':
    parse_timetables(TIMETABLE_DIR, OUT_FILE)
