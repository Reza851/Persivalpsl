import os
import sqlite3
import time

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

TOKEN = os.getenv("BOT_TOKEN")

DB = "users.db"

REWARD = 2000
COOLDOWN = 6 * 60 * 60


def database():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        coins INTEGER DEFAULT 0,
        last_claim INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()


def add_user(user_id):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute(
        "INSERT OR IGNORE INTO users(user_id) VALUES(?)",
        (user_id,)
    )

    conn.commit()
    conn.close()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    add_user(user.id)

    keyboard = [
        [InlineKeyboardButton("🎁 دریافت سکه", callback_data="claim")],
        [InlineKeyboardButton("💰 موجودی من", callback_data="balance")],
        [InlineKeyboardButton("👥 دعوت دوستان", callback_data="invite")],
        [InlineKeyboardButton("🔗 اتصال کیف پول", callback_data="wallet")],
        [InlineKeyboardButton("📢 کانال", url="https://t.me/YourChannel")]
    ]

    await update.message.reply_text(
        "🎁 Percival Airdrop\n\n"
        "به ایردراپ پرسیوال خوش آمدید.\n"
        "سکه دریافت کنید و دوستان خود را دعوت کنید.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    add_user(user_id)

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    if query.data == "claim":

        cur.execute(
            "SELECT last_claim FROM users WHERE user_id=?",
            (user_id,)
        )

        last = cur.fetchone()[0]
        now = int(time.time())

        if now - last >= COOLDOWN:

            cur.execute(
                "UPDATE users SET coins=coins+?, last_claim=? WHERE user_id=?",
                (REWARD, now, user_id)
            )

            conn.commit()

            await query.message.reply_text(
                "✅ 2000 سکه دریافت شد!"
            )

        else:
            remain = COOLDOWN - (now - last)
            hours = remain // 3600

            await query.message.reply_text(
                f"⏳ هنوز آماده نیست.\nزمان باقی‌مانده: {hours} ساعت"
            )


    elif query.data == "balance":

        cur.execute(
            "SELECT coins FROM users WHERE user_id=?",
            (user_id,)
        )

        coins = cur.fetchone()[0]

        await query.message.reply_text(
            f"💰 موجودی شما: {coins} سکه"
        )


    elif query.data == "invite":

        await query.message.reply_text(
            "👥 لینک دعوت شما:\n"
            f"https://t.me/YOUR_BOT_USERNAME?start={user_id}"
        )


    elif query.data == "wallet":

        await query.message.reply_text(
            "🔗 اتصال کیف پول در مرحله بعد اضافه می‌شود."
        )


    conn.close()


def main():

    database()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    app.run_polling()


if __name__ == "__main__":
    main()
