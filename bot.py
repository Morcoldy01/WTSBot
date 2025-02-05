import telebot
import sqlite3
import random
import string
import os

# --- 🔐 ТВОЙ ТОКЕН БОТА (ПОЛУЧИ В @BotFather) ---
BOT_TOKEN = "7928335218:AAF7yQ5UWmld2DjP9RA7uZjWwzmQoEywKQw"

# --- 🔑 ID АДМИНА (Твой Telegram ID, чтобы только ты мог выдавать токены) ---
ADMIN_ID = 1418032947  # Замени на свой ID

# --- 📝 СОЗДАЁМ БАЗУ SQLite ---
DB_PATH = "database.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id TEXT UNIQUE,
            token TEXT UNIQUE,
            ip TEXT
        )"""
    )
    conn.commit()
    conn.close()

init_db()

# --- 🤖 СОЗДАЁМ БОТА ---
bot = telebot.TeleBot(BOT_TOKEN)

# --- 🔢 ГЕНЕРАЦИЯ СЛУЧАЙНОГО ТОКЕНА ---
def generate_token():
    return ''.join(random.choices(string.ascii_uppercase, k=5))

# --- ✅ ВЫДАЧА ТОКЕНА (ТОЛЬКО ДЛЯ АДМИНА) ---
@bot.message_handler(commands=['give_token'])
def give_token(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⛔ У вас нет прав использовать эту команду!")
        return

    try:
        # Получаем Telegram ID пользователя
        args = message.text.split()
        if len(args) != 2:
            bot.reply_to(message, "⚠ Используйте: /give_token <telegram_id>")
            return

        telegram_id = args[1]
        token = generate_token()

        # Записываем в базу
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (telegram_id, token) VALUES (?, ?)", (telegram_id, token))
        conn.commit()
        conn.close()

        # Отправляем токен пользователю
        bot.send_message(telegram_id, f"🎫 Ваш токен: `{token}`")
        bot.reply_to(message, f"✅ Токен `{token}` выдан пользователю {telegram_id}")

    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {e}")

# --- 🏃‍♂️ ЗАПУСКАЕМ БОТА ---
print("🤖 Бот запущен!")
bot.polling()
