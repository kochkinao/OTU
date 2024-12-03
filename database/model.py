from sqlalchemy import Column, Integer, String, Time, ForeignKey
from sqlalchemy.dialects.postgresql import BOOLEAN
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


# Таблица для расписания пар
class ClassSchedule(Base):
    __tablename__ = 'class_schedule'
    pair_number = Column(Integer, nullable=False, primary_key=True)  # Номер пары
    start_time = Column(Time, nullable=False)  # Время начала
    end_time = Column(Time, nullable=False)  # Время конца

    def __repr__(self):
        return f"<ClassSchedule(pair_number={self.pair_number}, start_time={self.start_time}, end_time={self.end_time})>"


# Таблица для преподавателей
class Teacher(Base):
    __tablename__ = 'teachers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String, nullable=False, unique=True)  # ФИО преподавателя
    post = Column(String, nullable=False)   # Должность преподавателя

    lessons = relationship("Lesson", back_populates="teacher")  # Связь с таблицей Lesson

    def __repr__(self):
        return f"<Teacher(full_name={self.full_name})>"


# Таблица для расписания занятий
class Lesson(Base):
    __tablename__ = 'lessons'

    id = Column(Integer, primary_key=True, autoincrement=True)
    day_of_week = Column(Integer, nullable=False)  # День недели (1-5)
    room_number = Column(String, nullable=False)  # Номер аудитории
    is_even_week = Column(BOOLEAN, nullable=False)  # Четность недели
    is_practice = Column(BOOLEAN, nullable=False)  # Четность недели

    group_id = Column(Integer, ForeignKey('student_group.id'), nullable=False)  # Номер группы (ссылка на Group)
    pair_id = Column(Integer, ForeignKey('class_schedule.pair_number'), nullable=False)  # Номер пары (ссылка на ClassSchedule)
    teacher_id = Column(Integer, ForeignKey('teachers.id'), nullable=False)  # ID преподавателя (ссылка на Teacher)

    group = relationship("Group", back_populates="lessons")
    teacher = relationship("Teacher", back_populates="lessons")  # Обратная связь
    pair = relationship("ClassSchedule")  # Связь с таблицей ClassSchedule

    def __repr__(self):
        return (f"<Lesson(group_name={self.group_name}, day_of_week={self.day_of_week},"
                f" is_even_week={self.is_even_week}, room_number={self.room_number})>")

class Group(Base):
    __tablename__ = 'student_group'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)  # Название группы
    course = Column(Integer, nullable=False)  # Курс (1, 2, 3, 4 и т.д.)
    faculty = Column(String, nullable=True)  # Полное название факультета

    lessons = relationship("Lesson", back_populates="group")  # Связь с таблицей Lesson

    def __repr__(self):
        return f"<Group(name={self.name}, course={self.course}, faculty_short={self.faculty_short})>"
