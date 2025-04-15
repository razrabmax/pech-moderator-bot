import logging
import re
import asyncio
from collections import defaultdict
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import CommandStart
from aiogram.utils import executor
import os

API_TOKEN = os.getenv("API_TOKEN")

if not API_TOKEN:
    raise ValueError("❌ Переменная окружения API_TOKEN не установлена. Установи её в Railway или локально.")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_warnings = defaultdict(int)

bad_words = ['блять', 'сука', 'нахуй', 'ебать', 'пизда', 'хуй', 'гандон', 'мразь', 'даун']

def contains_link(text):
    return bool(re.search(r"(http[s]?://|t\.me/|@\w+|\w+\.\w{2,})", text))

@dp.message_handler(content_types=types.ContentType.TEXT)
async def handle_messages(message: types.Message):
    if message.chat.type not in ["group", "supergroup"]:
        return

    text = message.text.lower()
    user_id = message.from_user.id
    chat_id = message.chat.id
    username = message.from_user.full_name

    if contains_link(text):
        try:
            await message.delete()
            await bot.kick_chat_member(chat_id, user_id)
            await message.answer(f"🚫 {username} был забанен за отправку ссылок.")
        except Exception as e:
            logging.warning(f"Ошибка при кике за ссылку: {e}")
        return

    if any(word in text for word in bad_words):
        user_warnings[user_id] += 1
        await message.delete()

        if user_warnings[user_id] >= 3:
            try:
                await bot.kick_chat_member(chat_id, user_id)
                await message.answer(f"💥 {username} был забанен за 3 предупреждения (мат).")
            except Exception as e:
                logging.warning(f"Ошибка при бане: {e}")
        else:
            await message.answer(f"⚠️ {username}, не матерись! Предупреждение {user_warnings[user_id]}/3")

@dp.message_handler(CommandStart())
async def start_cmd(message: types.Message):
    await message.reply("🤖 Печ Модератор на страже порядка! Добавь меня в группу и выдай права админа.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
