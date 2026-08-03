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

ADMIN_ID = 8181107477
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
        claims INTEGER DEFAULT 0,
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

    user_id = update.effective_user.id
    add_user(user_id)

    keyboard = [
    [InlineKeyboardButton("🎁 دریافت سکه", callback_data="claim")],
    [InlineKeyboardButton("💰 موجودی من", callback_data="balance")],
    [InlineKeyboardButton("👤 پروفایل من", callback_data="profile")],
    [InlineKeyboardButton("📜 قوانین ایردراپ", callback_data="rules")],
    [InlineKeyboardButton("🔗 اتصال کیف پول", callback_data="wallet")]
]

if user_id == ADMIN_ID:
    keyboard.append(
        [InlineKeyboardButton("👑 مدیریت", callback_data="admin")]
    )

    await update.message.reply_text(
        "🎁 Percival Airdrop\n\n"
        "به ایردراپ پرسیوال خوش آمدید.\n"
        "هر ۶ ساعت ۲۰۰۰ سکه دریافت کنید.",
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
                """
                UPDATE users
                SET coins=coins+?,
                    claims=claims+1,
                    last_claim=?
                WHERE user_id=?
                """,
                (REWARD, now, user_id)
            )

            conn.commit()

            await query.message.reply_text(
                "✅ ۲۰۰۰ سکه دریافت شد."
            )

        else:
            remain = COOLDOWN - (now - last)
            hours = remain // 3600

            await query.message.reply_text(
                f"⏳ هنوز آماده نیست.\n"
                f"زمان باقی‌مانده: {hours} ساعت"
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


    elif query.data == "profile":

        cur.execute(
            "SELECT coins, claims FROM users WHERE user_id=?",
            (user_id,)
        )

        data = cur.fetchone()

        await query.message.reply_text(
            "👤 پروفایل Percival\n\n"
            f"💰 موجودی: {data[0]} سکه\n"
            f"🎁 تعداد دریافت: {data[1]} بار\n"
            f"🆔 شناسه: {user_id}"
        )


    elif query.data == "rules":

        await query.message.reply_text(
            "📜 قوانین Percival Airdrop\n\n"
            "• هر کاربر هر ۶ ساعت ۲۰۰۰ سکه دریافت می‌کند.\n"
            "• دعوت دوستان وجود ندارد.\n"
            "• همه کاربران شرایط یکسان دارند."
        )


    elif query.data == "wallet":

        await query.message.reply_text(
            "🔗 اتصال کیف پول در مراحل بعد اضافه خواهد شد."
        )


    conn.close()




elif query.data == "admin":

    if user_id != ADMIN_ID:
        await query.message.reply_text("⛔ دسترسی ندارید.")
        return

    cur.execute("SELECT COUNT(*) FROM users")
    users = cur.fetchone()[0]

    cur.execute("SELECT SUM(coins) FROM users")
    coins = cur.fetchone()[0] or 0

    cur.execute("SELECT SUM(claims) FROM users")
    claims = cur.fetchone()[0] or 0

    await query.message.reply_text(
        "👑 پنل مدیریت Percival\n\n"
        f"👥 کاربران: {users}\n"
        f"🪙 مجموع سکه‌ها: {coins}\n"
        f"🎁 تعداد دریافت‌ها: {claims}"
    )

def main():

    database()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    app.run_polling()


if __name__ == "__main__":
    main()
