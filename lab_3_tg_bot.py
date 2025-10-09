import asyncio
from os import environ

from dotenv import load_dotenv
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatAction
from telegram.ext import MessageHandler, filters, ContextTypes, ApplicationBuilder, CommandHandler, CallbackQueryHandler
from openai import OpenAI, RateLimitError

load_dotenv()

tg_bot_access_token = environ.get("kpi_test_bot", '')
chat_access_token = environ.get("chat_accessToken", '')
queue = asyncio.Queue()
tg_bot = Bot(token=tg_bot_access_token)
base_chat_url = environ.get("CHATGPT_BASE_URL", '')
API_KEY = environ.get("API_KEY", '')

client = OpenAI(api_key=API_KEY)


class ChatBot:
    def ask(self, text):
        response = client.chat.completions.create(
            # model="gpt-4o-mini",
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": text}]
        )
        return response.choices[0].message.content


chat_bot = ChatBot()


async def chatgpt_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        text = update.message.text
        reply = chat_bot.ask(text)
    except RateLimitError:
        reply = "Out of quota, please try again later."

    await update.message.reply_text(reply)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Student", callback_data='1'),
            InlineKeyboardButton("IT Technologies", callback_data='2')
        ],
        [
            InlineKeyboardButton("Contacts", callback_data='3'),
            InlineKeyboardButton("AI prompt", callback_data='ai_chat')
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Please choose an option:', reply_markup=reply_markup)


async def show_main_menu(query):
    keyboard = [
        [
            InlineKeyboardButton("Student", callback_data='1'),
            InlineKeyboardButton("IT Technologies", callback_data='2')
        ],
        [
            InlineKeyboardButton("Contacts", callback_data='3'),
            InlineKeyboardButton("AI prompt", callback_data='ai_chat')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Please choose an option:", reply_markup=reply_markup)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    selected_option = query.data

    # Back to main menu
    if selected_option == 'back':
        await show_main_menu(query)
        return

    # Handle each option
    if selected_option == '1':
        response = "Yuri Yefr IP_z21."
    elif selected_option == '2':
        response = "IT technologies is da best."
    elif selected_option == '3':
        response = "Contact via email yuryyefr@gmail.com."
    elif selected_option == 'ai_chat':
        response = "Welcome to chat."
    else:
        response = "Unknown option selected."

    # Adding back button
    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data='back')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text=response, reply_markup=reply_markup)


# --- Build and run the bot ---
app = ApplicationBuilder().token(tg_bot_access_token).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatgpt_reply))

if __name__ == '__main__':
    app.run_polling()
