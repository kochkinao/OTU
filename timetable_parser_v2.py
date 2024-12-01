import pdfplumber
import pandas as pd
import re


class TimetablePDFParser:
    def parse_pdf(self, filepath: str) -> pd.DataFrame:
        # Открываем файл расписания
        with pdfplumber.open(filepath) as pdf:
            first_page = pdf.pages[0]  # Указываем страницу с расписанием
            table_data = first_page.extract_table()

        if not table_data:
            raise ValueError(f"Таблица не извлечена из PDF: {filepath}")
        print("Извлечённые данные таблицы:", table_data)

        # Преобразуем в полученные данные в dataframe
        df = pd.DataFrame(table_data)
        df = df.drop(0)

        # Приводим названия столбцов к единому виду
        df.columns = df.iloc[0].fillna("").str.replace(r'\s+', ' ', regex=True).str.strip()
        df = df.drop(0).reset_index(drop=True)

        # Установка названий групп в качестве названий столбцов
        df.columns = df.iloc[0]
        df.rename(columns={'Время | Группа': 'Время'}, inplace=True)
        df = df.drop(1).reset_index(drop=True)

        df['День недели'] = df['День недели'].apply(lambda x: x.replace('\n', '').capitalize() if x else None)

        df['День недели'] = df['День недели'].ffill()

        result_df = pd.DataFrame(columns=['Группа', 'День недели', 'Время', 'Занятие'])

        # Парсим все пары отдельно
        for group in df.columns[2:]:
            for week_day, time, lesson in zip(df['День недели'], df['Время'], df[group]):
                # result_df.loc[len(result_df)] =
                print(self.parse_lesson_info(lesson))

        return result_df


if __name__ == '__main__':
    parser = TimetablePDFParser()
    df = parser.parse_all_pdfs(["timetables/3-kurs-strf-ibio-ekf-got-14.10.pdf"])
    df.to_csv('timetable_data.csv', index=False)
