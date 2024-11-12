import pdfplumber
import pandas as pd


class TimetablePDFParser:
    def parse_all_pdfs(self, filepaths: list[str]) -> pd.DataFrame:
        df = pd.DataFrame(columns=['Группа', 'День недели', 'Время', 'Занятие'])
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

        # Преобразуем в полученные данные в dataframe
        df = pd.DataFrame(table_data)
        df = df.drop(0)

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
                if not lesson:
                    lesson = None
                result_df.loc[len(result_df)] = {
                    'Группа': group,
                    'День недели': week_day,
                    'Время': time,
                    'Занятие': lesson,
                }

        return result_df


if __name__ == '__main__':
    parser = TimetablePDFParser()
    df = parser.parse_all_pdfs(["timetables/3-kurs-strf-ibio-ekf-got-14.10.pdf"])
    df.to_csv('timetable_data.csv')
