import pdfplumber
import pandas as pd

class TimetablePDFParser:
    def __init__(self):
        ...

    def parse_pdf(self, filepath: str):

        # Открываем файл расписания
        with pdfplumber.open(filepath) as pdf:
            first_page = pdf.pages[0]  # Указываем страницу с расписанием
            table_data = first_page.extract_table()

        # Преобразуем в полученные данные в dataframe
        df = pd.DataFrame(table_data)
        df = df.drop(0)

        # Установка названий групп в качестве названий столбцов
        df.columns = df.iloc[0]
        df.rename(columns={'Время | Группа': 'Время'}, inplace=True)
        df = df.drop(1).reset_index(drop=True)

        df['День недели'] = df['День недели'].apply(lambda x: x.replace('\n', '').capitalize() if x else None)

        df['День недели'] = df['День недели'].ffill()
        print(df[['День недели', 'Время']])

        # Парсим все пары отдельно
        for group in df.columns[2:]:
            print('-'*40)
            print(group)
            for day, time, lesson in zip(df['День недели'], df['Время'], df[group]):
                if not lesson:
                    lesson = None
                print(lesson)



if __name__ == '__main__':
    parser = TimetablePDFParser()
    parser.parse_pdf("timetables/3-kurs-strf-ibio-ekf-got-14.10.pdf")