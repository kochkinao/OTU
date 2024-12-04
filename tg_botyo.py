import asyncio

from aiogram import Bot, Dispatcher
from aiogram import F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.chat_action import ChatActionSender
from dotenv import load_dotenv

from database.db_manager import DbManager
from settings import DB_URL, TG_API_KEY

load_dotenv()

# Инициализация бота и базы данных
bot = Bot(token=TG_API_KEY)
dp = Dispatcher(storage=MemoryStorage())
db_manager = DbManager(DB_URL)

# Глобальные переменные
selected_group = ""
selected_teacher = ""
week_type = ""

class Form(StatesGroup):
    is_student = State()
    group = State()
    fio = State()
    is_even_week = State()

choose_teacher_or_student_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='Студент'), KeyboardButton(text='Преподаватель')]], resize_keyboard=True
)


# Команда /start
@dp.message(CommandStart())
async def send_welcome(message: Message, state: FSMContext):
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        await asyncio.sleep(1)
        await message.answer("Кто ты, воин?", reply_markup=choose_teacher_or_student_keyboard)
    await state.set_state(Form.is_student)


# Начальный выбор: группа или преподаватель


@dp.message(F.text.in_(["Студент", "Преподаватель"], Form.is_student))
async def initial_choice(message: Message, state: FSMContext):
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        choice = message.text.lower()
        if choice == "студент":
            await state.update_data(is_student=True)
            await message.answer("Введите название группы (например, АГС-22-1)", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
            await state.set_state(Form.fio)
        elif choice == "преподаватель":
            await state.update_data(is_student=False)
            await message.answer("Введите фамилию", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
            await state.set_state(Form.group)


@dp.message(F.text, Form.group)
async def handle_group(message: Message, state: FSMContext):
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        group = db_manager.find_group_by_name(message.text.upper())
        if group:
            await state.update_data(group_name=group.name)
            await message.answer("За какую неделю хотите расписание?")
            await state.set_state(Form.is_even_week)
        else:
            await message.answer("Нет такой группы, в названии ошибка!")

@dp.message(F.text, Form.group)
async def handle_fio(message: Message, state: FSMContext):
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        second_name = message.text.capitalize()
        full_name = db_manager.find_teacher_names(second_name)
        if full_name and len(full_name) == 1:
            await state.update_data(full_name=full_name)
            await message.answer("За какую неделю хотите расписание?")
            await state.set_state(Form.is_even_week)
        elif full_name:
            await message.answer()

        if gr:
            await state.update_data(group_name=group.name)
            await state.set_state(Form.is_even_week)
        else:
            await message.answer("Нет такой группы, в названии ошибка!")


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
# async def update_schedule():
#     parse_timetables(db_manager, SOURCE_DIR)


async def main():
    # update_schedule()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
