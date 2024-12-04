import os

import pdfplumber
import pandas as pd

from settings import SOURCE_DIR


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


class TimetablePDFParser:
    def parse_pdf(self, filepath: str) -> tuple[pd.DataFrame, list[str], set[str]]:
        # Открываем файл расписания
        with pdfplumber.open(filepath) as pdf:
            first_page = pdf.pages[0]  # Указываем страницу с расписанием
            table_data = first_page.extract_table()

        if not table_data:
            raise ValueError(f"Таблица не извлечена из PDF: {filepath}")
        # print("Извлечённые данные таблицы:", table_data)
        while table_data[0][0].lower() != 'день недели':
            table_data.pop(0)

        # Преобразуем данные в DataFrame
        df = pd.DataFrame(table_data)

        # Приводим названия столбцов к единому виду
        df.columns = df.iloc[0].fillna("").str.replace(r'\s+', ' ', regex=True).str.strip()
        df = df.drop(0).reset_index(drop=True)

        # Переименование столбца "Время | Группа"
        for col in df.columns:
            if 'время' in col.lower():
                df.rename(columns={col: 'Время'}, inplace=True)
                break

        if 'Время' not in df.columns:
            print("Доступные столбцы:", df.columns.tolist())
            raise ValueError("Столбец 'Время' отсутствует!")

        # Проверка столбца 'День недели'
        for col in df.columns:
            if 'день' in col.lower():
                df.rename(columns={col: 'День недели'}, inplace=True)
                break

        if 'День недели' not in df.columns:
            print("Доступные столбцы:", df.columns.tolist())
            raise ValueError("Столбец 'День недели' не найден даже после обработки!")

        # Обработка столбца 'День недели'
        df['День недели'] = df['День недели'].apply(lambda x: x.replace('\n', '').capitalize() if x else None)
        df['День недели'] = df['День недели'].ffill()
        # print("DataFrame после преобразования:", df.head())

        group_names = []
        pair_times = set()
        result_df = pd.DataFrame(columns=['group', 'week_day', 'time', 'lesson'])

        # Парсим все пары отдельно
        for group in df.columns[2:]:
            group_names.append(group)
            for week_day, time, lesson in zip(df['День недели'], df['Время'], df[group]):
                if not lesson:
                    lesson = None
                result_df.loc[len(result_df)] = {
                    'group': group,
                    'week_day': week_day,
                    'time': time.replace('.', ':'),
                    'lesson': lesson,
                }
                pair_times.add(time.replace('.', ':'))

        result_df[['start_time', 'end_time']] = result_df['time'].str.split('-', expand=True)
        result_df = result_df.drop(columns='time')
        # print("Доступные столбцы:", df.columns.tolist())
        return result_df, group_names, pair_times



if __name__ == '__main__':
    parser = TimetablePDFParser()
    for pdf in list_files_in_directory(SOURCE_DIR):
        df = parser.parse_pdf(pdf)
