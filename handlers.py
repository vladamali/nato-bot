import time
import logging

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove

from commons import GetStatistics, create_keyboard, load_data


countries, statistics, data = load_data('statistics.csv')
countries_str = '\n'.join(f"{i + 1}. {c}" for i, c in enumerate(countries))

stats_kb = create_keyboard(statistics)

async def start_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    user_name = message.from_user.username
    logging.info(f'{time.asctime()}: {user_id} @{user_name}: {message.text}')

    await state.finish()
    await message.answer(
        f"Привет, {user_full_name}! 👋\n"
        "Я помогу получить тебе интересующую статистику по странам НАТО.\n"
        "Выбери информацию, которую хочешь получить "
        "или введи /cancel для отмены",
        reply_markup=stats_kb)
    await state.set_state(GetStatistics.waiting_for_stat.state)


async def cancel_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = message.from_user.username
    logging.info(f'{time.asctime()}: {user_id} @{user_name}: {message.text}')

    await state.finish()
    await message.answer("Действие отменено. Введи /start, чтобы начать",
                         reply_markup=types.ReplyKeyboardRemove())


async def country_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = message.from_user.username
    logging.info(f'{time.asctime()}: {user_id} @{user_name}: {message.text}')

    if message.text not in statistics:
        await message.answer("Пожалуйста, выбери статистику на клавиатуре "
                             "или введи /cancel для отмены")
        return
    await state.update_data(statistic=message.text)
    await state.set_state(GetStatistics.waiting_for_country.state)
    await message.answer("Теперь введи номер страны:\n"
                         f"{countries_str}",
                         reply_markup=ReplyKeyboardRemove())


async def stat_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    user_name = message.from_user.username
    logging.info(f'{time.asctime()}: {user_id} @{user_name}: {message.text}')

    number = int(message.text) if message.text.isdecimal() else None
    if number and number in range(1, len(countries) + 1):
        await state.update_data(country = number - 1)
        user_data = await state.get_data()
        await message.answer(
            f"Страна: {countries[user_data['country']]}\n"
            f"{user_data['statistic']}: "
            f"{data[user_data['statistic']][user_data['country']]}",
            reply_markup=stats_kb)
        await message.answer("Выбери следующую статистику или введи /cancel "
                             "для отмены")
        await state.set_state(GetStatistics.waiting_for_stat.state)
    else:
        await message.answer("Пожалуйста, введи номер страны из списка выше "
                             "или введи /cancel для отмены")
        return


async def default_handler(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.username
    logging.info(f'{time.asctime()}: {user_id} @{user_name}: {message.text}')
    await message.answer("Я тебя не понимаю 😔\n"
                         "Введи /start, чтобы начать")


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start_handler, commands=["start"], state='*')
    dp.register_message_handler(cancel_handler, commands=["cancel"], state='*')
    dp.register_message_handler(country_handler,
                                state=GetStatistics.waiting_for_stat)
    dp.register_message_handler(stat_handler,
                                state=GetStatistics.waiting_for_country)
    dp.register_message_handler(default_handler)
