import os

from timetable_parser import TimetablePDFParser

TIMETABLE_DIR = 'timetables'
OUT_FILE = 'timetable_data.csv'


def list_files_in_directory(directory_path):
    file_paths = []
    # Получаем список всех файлов и папок в указанной папке
    for file_name in os.listdir(directory_path):
        # Строим полный путь к файлу
        file_path = os.path.join(directory_path, file_name)
        # Проверяем, является ли это файлом
        if os.path.isfile(file_path) and file_name.endswith('.pdf'):
            file_paths.append(file_path)
    return file_paths


if __name__ == '__main__':
    parser = TimetablePDFParser()
    files = list_files_in_directory(TIMETABLE_DIR)
    df = parser.parse_all_pdfs(filepaths=files)
    df.to_csv(OUT_FILE, index=False)
