import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart,Command
from aiogram.types import Message
import os
import openai
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


print(TELEGRAM_BOT_TOKEN)

#configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()




@dp.message(Command('start','help'))

async def command_start_handler(message: types.Message):
    """
    This handler receives messages with `/start` or  `/help `command
    """
    await message.reply("Hi, I am a bot powered by sX00.")
    


async def main():
    # Start polling
    await dp.start_polling(bot, skip_updates=True)

@dp.message()
async def echo_handler(message: types.Message):
    await message.answer("I received your message!")

if __name__ == "__main__":
    asyncio.run(main())
    #For aiogram v3: Use asyncio.run(main()) to properly await your coroutine.

