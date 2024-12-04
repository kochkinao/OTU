import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from aiogram import F
from dotenv import load_dotenv
from database.db_manager import DbManager
from lesson_parser import parse_lesson
from parse_timetables import parse_timetables
from settings import DB_URL, SOURCE_DIR

load_dotenv()

# Инициализация бота и базы данных
bot = Bot(token=os.getenv("TG_API_KEY"))
dp = Dispatcher()
db_manager = DbManager(DB_URL)

# Глобальные переменные
selected_group = ""
selected_teacher = ""
week_type = ""


# Команда /start
@dp.message(Command("start"))
async def send_welcome(message: Message):
    await message.answer(
        "Привет! Введите 'группа' для поиска по группе или 'преподаватель' для поиска по преподавателю."
    )


# Начальный выбор: группа или преподаватель
@dp.message(F.text.in_(["группа", "преподаватель"]))
async def initial_choice(message: Message):
    choice = message.text.lower()
    if choice == "группа":
        await message.answer("Введите название вашей группы (например, АГС-22-1):")
    elif choice == "преподаватель":
        await message.answer("Введите фамилию преподавателя (например, Иванов):")


# Обработка ввода группы или преподавателя

@dp.message(lambda message: message.text and len(message.text) > 2)
async def handle_input(message: Message):
    global selected_group, selected_teacher

    input_text = message.text.strip()

    # Проверка: это группа или преподаватель
    if db_manager.is_valid_group(input_text):
        selected_group = input_text
        await message.answer(
            f"Группа {selected_group} выбрана. Теперь выберите тип недели (четная/нечетная):"
        )
    elif db_manager.is_valid_teacher(input_text):
        selected_teacher = input_text
        await message.answer(
            f"Преподаватель {selected_teacher} выбран. Теперь выберите тип недели (четная/нечетная):"
        )
    else:
        await message.answer(
            "Неверный ввод. Убедитесь, что вы ввели корректное название группы или фамилию преподавателя. Попробуйте снова."
        )


# Выбор типа недели
@dp.message(F.text.in_(["четная", "нечетная"]))
async def handle_week_type(message: Message):
    global week_type
    week_type = "even" if message.text.lower() == "четная" else "odd"

    if selected_group:
        await message.answer(
            f"Выбрана {message.text} неделя. Введите день недели для получения расписания (например, Понедельник):"
        )
    elif selected_teacher:
        await message.answer(
            f"Выбрана {message.text} неделя. Введите день недели для получения расписания преподавателя (например, Понедельник):"
        )


# Выбор дня недели
@dp.message(F.text.in_(["понедельник", "вторник", "среда", "четверг", "пятница"]))
async def handle_day_selection(message: Message):
    day = message.text

    if selected_group:
        lessons = db_manager.get_daily_schedule(group_name=selected_group, day=day, week_type=week_type)
        if lessons:
            schedule = "\n".join([f"{lesson.pair.start_time} - {lesson.subject}" for lesson in lessons])
            await message.answer(schedule)
        else:
            await message.answer("Для этого дня расписания не найдено.")
    elif selected_teacher:
        lessons = db_manager.get_teacher_schedule(teacher_name=selected_teacher, day=day, week_type=week_type)
        if lessons:
            schedule = "\n".join(
                [f"{lesson.pair.start_time} - {lesson.group_name}: {lesson.subject}" for lesson in lessons])
            await message.answer(schedule)
        else:
            await message.answer("Для этого дня расписания преподавателя не найдено.")


# Обработка неверного ввода
@dp.message()
async def handle_invalid_input(message: Message):
    await message.answer(
        "Неверный ввод. Пожалуйста, следуйте инструкциям и попробуйте снова."
    )


# Запуск обновления расписания
async def update_schedule():
    parse_timetables(db_manager, SOURCE_DIR)


async def main():
    await update_schedule()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
