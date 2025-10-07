import asyncio
from os import environ

from dotenv import load_dotenv
from telegram import Bot, Update
from telegram.constants import ChatAction
from telegram.ext import Updater, MessageHandler, filters, ContextTypes, ApplicationBuilder

load_dotenv()

tg_bot_access_token = environ.get("kpi_test_bot", '')
chat_access_token = environ.get("chat_accessToken", '')
queue = asyncio.Queue()
tg_bot = Bot(token=tg_bot_access_token)
updater = Updater(tg_bot, queue)
base_chat_url = environ.get("CHATGPT_BASE_URL", '')
API_KEY = environ.get("API_KEY", '')
# chat_bot = Chatbot(config={'access_token': chat_access_token}, base_url=base_chat_url)
# chat_bot = Chatbot(config={'access_token': chat_access_token})
from openai import OpenAI, RateLimitError

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

app = ApplicationBuilder().token(tg_bot_access_token).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatgpt_reply))
# while True:
app.run_polling()