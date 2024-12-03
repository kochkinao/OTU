from datetime import time

from sqlalchemy import create_engine, se
from sqlalchemy.orm import sessionmaker

from settings import DB_URL

from model import Base, Group, Teacher, ClassSchedule


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

if __name__ == '__main__':
    DbManager(DB_URL)
