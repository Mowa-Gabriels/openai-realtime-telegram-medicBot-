import asyncio
import logging
import sys
from os import getenv
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart,Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton,CallbackQuery,KeyboardButton,ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import os
import openai
from dotenv import load_dotenv
from openai import OpenAI
from database import save_booking  # Import function to save bookings





load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_CHAT_ID = " ADMIN_CHAT_ID" # Replace with your Telegram Admin Chat ID

SYSTEM_PROMPT = (
    "You are sXMed AI, a high-level medical practitioner;a senior radiologist with 30 years in practice. created by s00. "
    "Your role is to provide clear, evidence-based information on radiology-related topics and diagnosis. "
    "you can also recommend possible diagnosis, test and scans by asking patient relevant questions"
    "Always include a disclaimer such as 'This is not medical advice and is for informational purposes only'"
     "to book a consult or diagnostic appointment, let them enter /consult'  also for other services click /menu"

)

class Reference:
    '''
    A class to store previously response from the openai API
    '''

    def __init__(self) -> None:
        self.response = ""



reference = Reference()
model_name = "gpt-4o-mini"
logging.basicConfig(level=logging.INFO)
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






@dp.message(Command('consult'))
async def command_consult_handler(message: types.Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            
            [InlineKeyboardButton(text="📅 Book Consultation", callback_data="book_consult")],
            [InlineKeyboardButton(text="🩺 Book Diagnostic Appointment", url="https://your-diagnostic-link.com")]
       
        ]
    )
    await message.reply(
        "Hi, I'm sXMed AI, your medical assistant. Click below to book a consultation.",
        reply_markup=keyboard
    )


# Define states for user input
class BookingForm(StatesGroup):
    full_name = State()
    age = State()
    gender = State()
    phone_no = State()
    symptoms = State()
    confirm = State()

# Handle Consultation Booking Button
@dp.callback_query(lambda c: c.data == "book_consult")
async def book_consult_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Please enter your full name:")
    await state.set_state(BookingForm.full_name)
    await callback.answer()


# Capture Full Name
@dp.message(BookingForm.full_name)
async def process_full_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer("Great! Now, enter your age:")
    await state.set_state(BookingForm.age)

# Capture Age
@dp.message(BookingForm.age)
async def process_age(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("What symptoms are you experiencing?")
    await state.set_state(BookingForm.gender)

# Capture Gender
@dp.message(BookingForm.gender)
async def process_age(message: types.Message, state: FSMContext):
    await state.update_data(gender=message.text)
    await message.answer("What is your gender?")
    await state.set_state(BookingForm.phone_no)

# Capture PhoneNo
@dp.message(BookingForm.phone_no)
async def process_age(message: types.Message, state: FSMContext):
    await state.update_data(phone_no=message.text)
    await message.answer("Enter your phone number?")
    await state.set_state(BookingForm.symptoms)

# Capture Symptoms & Confirm Booking
@dp.message(BookingForm.symptoms)
async def process_symptoms(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    await state.update_data(symptoms=message.text)

    # Confirm Details
    confirmation_message = (
        f"✅ Please confirm your details!\n\n\n\n"
        f"👤 Name: {user_data['full_name']}\n"
        f"🔢 Age: {user_data['age']}\n"
        f"Gender: {user_data['gender']}\n"
        f"Phone Number: {user_data['phone_no']}\n"
        f"🤒 Symptoms: {message.text}\n\n"
       "Click Confirm to proceed or Edit Info to modify your details."
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Confirm", callback_data="confirm_booking")],
            [InlineKeyboardButton(text="✏️ Edit Info", callback_data="edit_booking")]
        ]
    )

    await message.answer(confirmation_message, reply_markup=keyboard)
    await state.set_state(BookingForm.confirm)

# Handle Confirmation
@dp.callback_query(lambda c: c.data == "confirm_booking")
async def confirm_booking(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()

    # Save booking in the database
    save_booking(user_data["full_name"], user_data["age"], user_data["gender"], user_data["phone_no"],user_data["symptoms"])

    # Notify Admin
    admin_message = (
        f"📩 New Booking Received!\n\n"
        f"👤 Name: {user_data['full_name']}\n"
        f"🔢 Age: {user_data['age']}\n"
        f"Gender: {user_data['gender']}\n"
        f"Phone Number: {user_data['phone_no']}\n"
        f"🤒 Symptoms: {user_data['symptoms']}\n\n"
        f"📅 Date: Pending Confirmation"
    )
    await bot.send_message(ADMIN_CHAT_ID, admin_message)  # Send notification to admin


    final_message = (
        f"🎉 Booking Confirmed!\n\n\n\n"
        f"👤 Name: {user_data['full_name']}\n"
        f"🔢 Age: {user_data['age']}\n"
        f"Gender: {user_data['gender']}\n"
        f"Phone Number: {user_data['phone_no']}\n"
        f"🤒 Symptoms: {user_data['symptoms']}\n\n"
        "A medical professional will contact you soon. ✅"
    )


    await callback.message.answer(final_message)
    await state.clear()  # Reset state
    await callback.answer()

# Handle Edit Info
@dp.callback_query(lambda c: c.data == "edit_booking")
async def edit_booking(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Let's restart the process. Please enter your full name:")
    await state.set_state(BookingForm.full_name)
    await callback.answer()





@dp.message(Command('help'))

async def command_help_handler(message: types.Message):

    """
    This handler receives messages with`/help `command
    """

    help_command = """
    "Hi, I'm sXMed AI, your high-level radiologist created by sX00. -" 
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


if __name__ == "__main__":
    asyncio.run(main())
    #For aiogram v3: Use asyncio.run(main()) to properly await your coroutine.

