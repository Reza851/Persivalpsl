
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام، ربات فعال است ✅")

token = os.getenv("BOT_TOKEN")

app = Application.builder().token(token).build()

app.add_handler(CommandHandler("start", start))

app.run_polling()
