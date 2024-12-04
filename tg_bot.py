import asyncio
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher
from aiogram import F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery
from aiogram.utils.chat_action import ChatActionSender
from dotenv import load_dotenv

from database.db_manager import DbManager
from database.model import Lesson
from settings import DB_URL, TG_API_KEY
from weekdays import get_week_day_name

load_dotenv()

# Инициализация бота и базы данных
bot = Bot(token=TG_API_KEY)
dp = Dispatcher(storage=MemoryStorage())
db_manager = DbManager(DB_URL)


class Form(StatesGroup):
    is_student = State()
    group = State()
    fio = State()
    is_even_week = State()


choose_teacher_or_student_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='Студент'), KeyboardButton(text='Преподаватель')]],
    resize_keyboard=True
)

back_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='Назад')]],
    resize_keyboard=True
)

choose_week_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='Текущая неделя')],
              [KeyboardButton(text='Чётная'), KeyboardButton(text='Нечётная')],
              [KeyboardButton(text='Назад')]],
    resize_keyboard=True
)


# Команда /start
@dp.message(CommandStart())
async def send_welcome(message: Message, state: FSMContext):
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        await message.answer("Кто ты, воин?", reply_markup=choose_teacher_or_student_keyboard)
    await state.set_state(Form.is_student)


# Начальный выбор: группа или преподаватель


@dp.message(F.text.in_(["Студент", "Преподаватель"]), Form.is_student)
async def initial_choice(message: Message, state: FSMContext):
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        choice = message.text.lower()
        if choice == "студент":
            await state.update_data(is_student=True)
            await message.answer("Введите название группы (например, АГС-22-1)", reply_markup=back_keyboard)
            await state.set_state(Form.group)
        elif choice == "преподаватель":
            await state.update_data(is_student=False)
            await message.answer("Введите фамилию", reply_markup=back_keyboard)
            await state.set_state(Form.fio)


@dp.message(F.text, Form.group)
async def handle_group(message: Message, state: FSMContext):
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        if message.text == 'Назад':
            await state.set_state(Form.is_student)
            await send_welcome(message=message, state=state)
        else:
            group = db_manager.find_group_by_name(message.text.upper())
            if group:
                await state.update_data(group_name=group.name)
                await message.answer("За какую неделю хотите расписание?", reply_markup=choose_week_keyboard)
                await state.set_state(Form.is_even_week)
            else:
                await message.answer("Нет такой группы, в названии ошибка!")


@dp.message(F.text, Form.fio)
async def handle_fio(message: Message, state: FSMContext):
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        if message.text == 'Назад':
            await state.set_state(Form.is_student)
            await send_welcome(message=message, state=state)
        else:
            second_name = message.text
            second_name = second_name.split(' ')
            second_name[0] = second_name[0].capitalize()
            second_name = ' '.join(second_name)
            full_name = db_manager.find_teacher_names(second_name)
            if full_name and len(full_name) == 1:
                await state.update_data(full_name=full_name[0])
                await message.answer("За какую неделю хотите расписание?", reply_markup=choose_week_keyboard)
                await state.set_state(Form.is_even_week)
            elif full_name:
                inline_keyboard = [[KeyboardButton(text=name)] for name in full_name]
                keyboard = ReplyKeyboardMarkup(keyboard=inline_keyboard, resize_keyboard=True)
                await message.answer('Выберите своё ФИО', reply_markup=keyboard)
            else:
                await message.answer('Не знаем такого')


@dp.callback_query(F.data.startswith('teachers_name:'))
async def handle_fio(call: CallbackQuery, state: FSMContext):
    async with ChatActionSender.typing(bot=bot, chat_id=call.message.chat.id):
        await state.update_data(full_name=call.data.split(':')[-1])
        await call.answer("За какую неделю хотите расписание?", reply_markup=choose_week_keyboard)
        await state.set_state(Form.is_even_week)


@dp.message(F.text, Form.is_even_week)
async def handle_week(message: Message, state: FSMContext):
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        data = await state.get_data()
        if message.text == 'Назад':
            if data['is_student']:
                await state.set_state(Form.group)
                await message.answer("Введите название группы (например, АГС-22-1)", reply_markup=back_keyboard)
            else:
                await state.set_state(Form.fio)
                await message.answer("Введите фамилию", reply_markup=back_keyboard)
        else:
            request = message.text
            if request == 'Текущая неделя':
                today = datetime.today()
                year = today.year if today.month >= 9 else today.year - 1
                sep_1 = datetime(year, 9, 1)
                if sep_1.weekday() >= 5:
                    sep_1 += timedelta(days=7 - sep_1.weekday())
                week = (today - sep_1).days // 7 + 1
                request = 'Чётная' if week % 2 == 0 else 'Нечётная'
            is_even_week = request == 'Нечётная'
            if data['is_student']:
                pairs = db_manager.get_weekly_group_pairs(group=data['group_name'], is_even_week=is_even_week)
                msg = await send_student_pairs(pairs, is_even_week=is_even_week, group_name=data['group_name'])
            else:
                pairs = db_manager.get_weekly_teacher_pairs(full_teacher_name=data['full_name'],
                                                            is_even_week=request == 'Нечётная')
                msg = await send_teacher_pairs(pairs, is_even_week=is_even_week)
            await message.answer(text=msg)


async def send_student_pairs(pairs: list[Lesson], is_even_week: bool, group_name: str) -> str:
    result = f'Расписание {"нечётной" if is_even_week else "чётной"} недели для группы {group_name}:\n'
    previous_pair: Lesson = None
    for pair in pairs:
        if pair.subject != 'Нет занятия':
            pair_string = f'        {pair.subject}\n'
        else:
            pair_string = '        Нет занятия\n'
        if pair.teacher and not pair.room_number:
            pair_string += f'        {pair.teacher} {"пр." if pair.is_practice else ""}\n'
        elif pair.teacher and pair.room_number:
            pair_string += f'        {pair.teacher} {"пр." if pair.is_practice else ""}   №{pair.room_number}\n'
        if not previous_pair or previous_pair.day_of_week != pair.day_of_week:
            result += f'\n{get_week_day_name(pair.day_of_week).capitalize()}:\n'
        if previous_pair and pair.pair_id == previous_pair.pair_id and previous_pair.day_of_week == pair.day_of_week:
            result += pair_string
        else:
            result += f'    {pair.pair.start_time.strftime(format="%H:%M")}-{pair.pair.end_time.strftime(format="%H:%M")}:\n'
            result += pair_string
        previous_pair = pair
    return result


async def send_teacher_pairs(pairs: list[Lesson], is_even_week: bool) -> str:
    result = f'Ваше расписание {"нечётной" if is_even_week else "чётной"} недели:\n'
    previous_pair: Lesson = None
    for pair in pairs:
        if pair.subject == 'Нет занятия':
            pair_string = '        Нет занятия\n'
        elif previous_pair and pair.pair_id == previous_pair.pair_id and pair.day_of_week == previous_pair.day_of_week:
            pair_string = f''
        elif pair.room_number:
            pair_string = f'        {pair.subject} {"пр." if pair.is_practice else ""} ауд. №{pair.room_number}\n'
        else:
            pair_string = f'        {pair.subject} {"пр." if pair.is_practice else ""}\n'
        pair_string += f'        {pair.group}\n'
        if not previous_pair or previous_pair.day_of_week != pair.day_of_week:
            result += f'\n{get_week_day_name(pair.day_of_week).capitalize()}:\n'
        if previous_pair and pair.pair_id == previous_pair.pair_id and previous_pair.day_of_week == pair.day_of_week:
            result += pair_string
        else:
            result += f'    {pair.pair.start_time.strftime(format="%H:%M")}-{pair.pair.end_time.strftime(format="%H:%M")}:\n'
            result += pair_string
        previous_pair = pair
    return result


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
