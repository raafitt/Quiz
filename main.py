import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F
from config import API_TOKEN
from data import quiz_data
from db_request import update_quiz_index, update_statistics, get_quiz_index, get_statistics,get_table_rows, create_table

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# Объект бота
bot = Bot(token=API_TOKEN)
# Диспетчер
dp = Dispatcher()

def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()

    for option in answer_options:
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data=option,
        ))

    builder.adjust(1)
    return builder.as_markup()

@dp.callback_query()
async def right_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    user_id=callback.from_user.id
    first_name=callback.from_user.first_name
   
    current_question_index = await get_quiz_index(user_id)
    correct_index = quiz_data[current_question_index]['correct_option']
    opts = quiz_data[current_question_index]['options']

    await callback.message.answer(f'Ваш ответ: {callback.data}')

    if callback.data != opts[correct_index]:
        correct_option = quiz_data[current_question_index]['correct_option']
        await callback.message.answer(f"Неправильно. Правильный ответ: {quiz_data[current_question_index]['options'][correct_option]}")
    else:
        point = await get_statistics(user_id)
        point += 1
        await update_statistics(user_id, point,first_name)
        await callback.message.answer('Верно')
    current_question_index += 1
    if current_question_index < len(quiz_data):
        await update_quiz_index(user_id, current_question_index,first_name)
        await send_quiz_question(user_id)
    else:
        point = await get_statistics(user_id)
        await callback.message.answer(f'Вы прошли весь квиз! Поздравляем!\nВы набрали {point} балла')
        #Получаем записи из таблицы
        table_rows=await get_table_rows()
        results=''
        for row in table_rows:
            first_name = row[3]
            results += f"{first_name} набрал {row[2]} балла\n"
        await callback.message.answer(f'Общая статистика игроков\n{results}')
        await update_quiz_index(user_id, 0, first_name)

async def send_quiz_question(user_id):
    current_question_index = await get_quiz_index(user_id)
    question = quiz_data[current_question_index]['question']
    options = quiz_data[current_question_index]['options']
    correct_option = quiz_data[current_question_index]['correct_option']

    await bot.send_message(
        chat_id=user_id,
        text=question,
        reply_markup=generate_options_keyboard(options, correct_option)
    )

async def get_question(message, user_id):
    current_question_index = await get_quiz_index(user_id)
    correct_index = quiz_data[current_question_index]['correct_option']
    opts = quiz_data[current_question_index]['options']
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)

async def new_quiz(message):
    user_id = message.from_user.id
    first_name=message.from_user.first_name
    current_question_index = 0
    point=0
    await update_statistics(user_id, point,first_name)
    await update_quiz_index(user_id, current_question_index,first_name)
    await get_question(message, user_id)

# Хэндлер на команду /quiz
@dp.message(F.text == "Начать игру")
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    await message.answer("Давайте начнем квиз!")
    await new_quiz(message)

async def main():
    await create_table()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
