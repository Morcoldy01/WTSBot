import sqlite3
import random
import string
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# --- 🔧 НАСТРОЙКИ ---
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"  # 🔥 Замени на свой токен бота из @BotFather
ADMIN_ID = 123456789  # 🔥 Замени на свой Telegram ID

# --- 📦 ЛОГИ ---
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- 📂 СОЗДАНИЕ БАЗЫ ---
def init_db():
    """Создаёт таблицу пользователей, если её нет."""
    conn = sqlite3.connect("database.db")
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

# --- 🔑 ГЕНЕРАЦИЯ ТОКЕНА ---
def generate_token():
    """Генерирует случайный токен из 5 букв."""
    return "".join(random.choices(string.ascii_uppercase, k=5))

# --- 💾 СОХРАНЕНИЕ ПОЛЬЗОВАТЕЛЯ ---
def save_user(telegram_id, token):
    """Сохраняет пользователя в базу."""
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO users (telegram_id, token) VALUES (?, ?)",
        (telegram_id, token),
    )
    conn.commit()
    conn.close()

# --- 👑 ПРОВЕРКА АДМИНА ---
def is_admin(update: Update):
    """Проверяет, является ли пользователь админом."""
    return update.message.from_user.id == ADMIN_ID

# --- 📌 ДОБАВЛЕНИЕ НОВОГО ПОЛЬЗОВАТЕЛЯ ---
def add_user(update: Update, context: CallbackContext):
    """Команда /adduser <telegram_id> (доступна только админу)"""
    if not is_admin(update):
        update.message.reply_text("⛔ У вас нет прав для выполнения этой команды.")
        return

    if not context.args:
        update.message.reply_text("❌ Используйте: /adduser <Telegram ID>")
        return

    user_id = context.args[0]
    token = generate_token()

    save_user(user_id, token)
    
    update.message.reply_text(f"✅ Пользователь {user_id} зарегистрирован.\n🔑 Токен: `{token}`")

    # Отправляем токен пользователю
    try:
        context.bot.send_message(chat_id=user_id, text=f"🔑 Ваш токен: `{token}`")
    except Exception as e:
        update.message.reply_text(f"⚠ Ошибка отправки токена пользователю: {e}")

# --- 🔍 ПРОВЕРКА ТОКЕНА ---
def check_token(update: Update, context: CallbackContext):
    """Команда /checktoken <токен> для проверки токена в базе."""
    if not context.args:
        update.message.reply_text("❌ Используйте: /checktoken <токен>")
        return

    token = context.args[0]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT telegram_id FROM users WHERE token = ?", (token,))
    result = cursor.fetchone()
    conn.close()

    if result:
        update.message.reply_text(f"✅ Токен действителен. Telegram ID: {result[0]}")
    else:
        update.message.reply_text("⛔ Неверный токен!")

# --- 🚀 ЗАПУСК БОТА ---
def main():
    """Запуск Telegram-бота."""
    init_db()  # Создаём базу, если её нет
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("adduser", add_user))  # Админ добавляет пользователя
    dp.add_handler(CommandHandler("checktoken", check_token))  # Проверка токена

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
