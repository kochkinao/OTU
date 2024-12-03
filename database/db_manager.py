import pprint
from datetime import time
from typing import Iterable

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.operators import like_op

from settings import DB_URL

from database.model import Base, Group, Teacher, ClassSchedule, Lesson
from weekdays import get_week_day_number

class DbManager:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)  # Создаем таблицы, если их еще нет
        self.Session = sessionmaker(bind=self.engine)

    def find_group_by_name(self, group_name: str):
        """
        Найти группу по имени.
        :param group_name: Название группы (например, 'ИВТ-21').
        :return: Объект Group или None, если группа не найдена.
        """
        with self.Session() as session:
            return session.query(Group).filter(Group.name == group_name).first()

    def find_teacher_by_name(self, teacher_name: str):
        """
        Найти преподавателя по имени.
        :param teacher_name: ФИО преподавателя (например, 'Иванов Иван Иванович').
        :return: Объект Teacher или None, если преподаватель не найден.
        """
        with self.Session() as session:
            return session.query(Teacher).filter(Teacher.full_name == teacher_name).first()

    def find_pair_by_start_time(self, start_time: time):
        """
        Найти пару по времени начала.
        :param start_time: Время начала пары (например, '08:00:00').
        :return: Объект ClassSchedule или None, если пара не найдена.
        """
        with self.Session() as session:
            return session.query(ClassSchedule).filter(ClassSchedule.start_time == start_time).first()

    def find_pair_by_number(self, number: int):
        with self.Session() as session:
            return session.query(ClassSchedule).filter(ClassSchedule.pair_number == number).first()

    def remove_all_lessons(self):
        with self.Session() as session:
            for lesson in session.query(Lesson).all():
                session.delete(lesson)
            session.commit()

    def find_teacher_names(self, part_of_full_name: str) -> Iterable[str]:
        """Получает на вход фамилию (или её часть), послде чего находит всех преподавателей с такой фамилией"""
        with self.Session() as session:
            full_names = session.query(Teacher.full_name).where(like_op(Teacher.full_name, f'{part_of_full_name}%')).all()
            full_names = [name[0] for name in full_names]
            return full_names

    def get_daily_group_pairs(self, group: str, day: str, is_even_week: bool):
        """Получает все пары группы за определённый день"""
        with self.Session() as session:
            lessons = session.query(Lesson).join(ClassSchedule).join(Group)\
                .where(Group.name == group.upper())\
                .where(Lesson.day_of_week == get_week_day_number(day))\
                .where(Lesson.is_even_week == is_even_week)\
                .order_by(Lesson.day_of_week, ClassSchedule.start_time).all()
            return lessons

    def save(self, obj):
        with self.Session() as session:
            session.add(obj)
            session.commit()

    def save_all(self, obj_list):
        with self.Session() as session:
            session.add_all(obj_list)
            session.commit()


if __name__ == '__main__':
    db_manager = DbManager(DB_URL)
    for i in db_manager.get_daily_group_pairs('ист-22-2', 'Понедельник', is_even_week=True):
        print(i.day_of_week, i.pair_id, i.subject)
