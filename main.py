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
from openai import OpenAI



load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

SYSTEM_PROMPT = (
    "You are sXMed AI, a high-level medical practitioner created by s00. "
    "Your role is to provide clear, evidence-based information on health-related topics. "
    "Always include a disclaimer such as 'This is not medical advice and is for informational purposes only; please consult a healthcare professional for personal advice.' "
    "If the question requires a diagnosis or personalized medical advice, remind the user to seek professional help."
)

class Reference:
    '''
    A class to store previously response from the openai API
    '''

    def __init__(self) -> None:
        self.response = ""



reference = Reference()
model_name = "gpt-4o-mini"

# Initialize bot and dispatcher
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


def clear_past():
    """A function to clear the previous conversation and context.
    """
    reference.response = ""

@dp.message(Command('exit'))
async def command_clear_handler(message: types.Message):
    """
    This handler clears messages with `/clear` command
    """
    await message.reply("Chats from pass conversation and context cleared.")



@dp.message(Command('start'))

async def command_start_handler(message: types.Message):
    """
    This handler receives messages with `/start` or  `/help `command
    """
    welcome_message = (
        "Hi, I'm sXMed AI, your high-level medical assistant created by sX00. "
        "I can provide you with information on various health-related topics. "
        "Remember, this is for informational purposes only and not a substitute for professional medical advice."
    )
    await message.reply(welcome_message)


@dp.message(Command('help'))

async def command_help_handler(message: types.Message):

    """
    This handler receives messages with`/help `command
    """

    help_command = """
    "Hi, I'm sXMed AI, your high-level medical assistant created by sX00. -" 
    /start - to start the conversation
    /clear - to clear the past conversation and context.
    /help - to get this help menu.
    I hope this helps. :)
    """
    await message.reply(help_command)
    
    

@dp.message()
async def echo_handler(message: types.Message):
    client = OpenAI(api_key=OPENAI_API_KEY)

    """
    Sends the user's message to the OpenAI GPT model and echoes the generated response.
    """
    user_input = message.text
    print(f">>> USER: \n\t{user_input}")
    try:
        # Call OpenAI's ChatCompletion API asynchronously.
        # Note: acreate is the async version of create (available in openai>=0.27.0).
        response = client.chat.completions.create(
        model=model_name,
        store=True,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content":user_input} #our query 
        ],
        temperature =0.6
        )

        # Extract GPT's reply from the response
        reply_text = response.choices[0].message.content

    except Exception as e:
        logging.exception("Error calling OpenAI API")
        reply_text = "Sorry, I encountered an error processing your request."

    print(f">>> chatGPT: \n\t{reply_text}")

    await message.answer(reply_text)


 

   




async def main():
    # Start polling
    await dp.start_polling(bot, skip_updates=True)




# @dp.message()
# async def echo_handler(message: types.Message):
#     await message.answer("I received your message!")

if __name__ == "__main__":
    asyncio.run(main())
    #For aiogram v3: Use asyncio.run(main()) to properly await your coroutine.

