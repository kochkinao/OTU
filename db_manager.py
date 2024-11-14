import pprint
from datetime import datetime, time
from typing import NamedTuple

import pandas as pd
import sqlalchemy

Weekday = str


class Lesson(NamedTuple):
    week_day: str
    time: str
    name: str


class ScheduleLoader:
    def __init__(self, db_url):
        self.db_engine = sqlalchemy.create_engine(db_url)
        self.df = self.read_schedule_file()

    @staticmethod
    def _parse_time_interval(time_str):
        start_time, end_time = time_str.split('-')
        start_datetime = datetime.strptime(start_time, '%H.%M')
        end_datetime = datetime.strptime(end_time, '%H.%M')
        return start_datetime, end_datetime

    @staticmethod
    def _make_time_interval(begin_time: time, end_time: time):
        return begin_time.strftime('%H:%M') + '-' + end_time.strftime('%H:%M')

    def read_schedule_file(self):
        df = pd.read_sql(sql='class', con=self.db_engine.connect())
        return df

    def get_daily_schedule(self, group: str, week_day: str) -> list[Lesson]:
        """Возвращает список занятий группы по заданноиу дню недели"""
        daily_lessons = []

        # Фильтруем по группе и дню недели и сортируем по времени
        filtered_df = self.df[(self.df['week_day'] == week_day) & (self.df['group'] == group)].sort_values(
            by='start_time')

        for _, row in filtered_df.iterrows():
            lesson = Lesson(
                week_day=row['week_day'],
                time=self._make_time_interval(row['start_time'], row['end_time']),
                name=row['lesson']
            )
            # Добавляем занятие в список для соответствующего дня недели
            daily_lessons.append(lesson)
        return daily_lessons

    def get_weekly_schedule(self, group) -> dict[Weekday, list[Lesson]]:
        """Возвращает словарь вида [День недели: Список занятий] для заданной группы"""
        weekly_lessons = {}
        for week_day in ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница']:
            weekly_lessons[week_day] = self.get_daily_schedule(group, week_day)
        return weekly_lessons


if __name__ == '__main__':
    loader = ScheduleLoader(db_url='postgresql://postgres:root@localhost:7546/shedule')

    daily_lessons = loader.get_daily_schedule(group='АГС-22-1', week_day='Понедельник')
    pprint.pp(daily_lessons)
    print()

    weekly_lessons = loader.get_weekly_schedule(group='АГС-22-1')
    pprint.pp(weekly_lessons)
