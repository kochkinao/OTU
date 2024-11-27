import pdfplumber
import pandas as pd


class TimetablePDFParser:
    def parse_all_pdfs(self, filepaths: list[str]) -> pd.DataFrame:
        df = pd.DataFrame(columns=['group', 'week_day', 'start_time', 'end_time', 'lesson'])
        for filepath in filepaths:
            new_data = self.parse_pdf(filepath)
            df = pd.concat([df, new_data])
        return df

    @staticmethod
    def parse_pdf(filepath: str) -> pd.DataFrame:
        # Открываем файл расписания
        with pdfplumber.open(filepath) as pdf:
            first_page = pdf.pages[0]  # Указываем страницу с расписанием
            table_data = first_page.extract_table()

        if not table_data:
            raise ValueError(f"Таблица не извлечена из PDF: {filepath}")
        print("Извлечённые данные таблицы:", table_data)

        # Преобразуем данные в DataFrame
        df = pd.DataFrame(table_data)
        print("DataFrame после преобразования:", df.head())

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

        # Создание результата
        result_df = pd.DataFrame(columns=['group', 'week_day', 'time', 'lesson'])

        # Парсим пары
        for group in df.columns[2:]:
            for week_day, time, lesson in zip(df['День недели'], df['Время'], df[group]):
                if not lesson:
                    lesson = None
                result_df.loc[len(result_df)] = {
                    'group': group,
                    'week_day': week_day,
                    'time': time.replace('.', ':'),
                    'lesson': lesson,
                }

        result_df[['start_time', 'end_time']] = result_df['time'].str.split('-', expand=True)
        result_df = result_df.drop(columns='time')
        print("Доступные столбцы:", df.columns.tolist())
        return result_df


if __name__ == '__main__':
    parser = TimetablePDFParser()
    df = parser.parse_all_pdfs(["timetables/3-kurs-strf-ibio-ekf-got-14.10.pdf"])
    df.to_csv('timetable_data.csv', index=False)
