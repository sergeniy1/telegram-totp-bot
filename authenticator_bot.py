from dotenv import load_dotenv
import os
import telebot
import pyotp
import json
import base64
from cryptography.fernet import Fernet
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Загружаем переменные из .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
ALLOWED_USER_ID = os.getenv("ALLOWED_USER_ID")
DATA_FILE = "totp_data.json"

if not ENCRYPTION_KEY:
    raise Exception("❌ В .env должен быть ENCRYPTION_KEY")

fernet = Fernet(ENCRYPTION_KEY.encode())
bot = telebot.TeleBot(TOKEN)

# Загрузка и расшифровка сохранённых данных
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "rb") as f:
        try:
            user_data = json.loads(fernet.decrypt(f.read()))
        except:
            user_data = {}
else:
    user_data = {}

# Сохраняем зашифрованные данные в файл
def save_data():
    with open(DATA_FILE, "wb") as f:
        f.write(fernet.encrypt(json.dumps(user_data).encode()))

# Проверка авторизации пользователя
def is_authorized(message):
    return str(message.chat.id) == str(ALLOWED_USER_ID)

@bot.message_handler(commands=['start'])
def start(message):
    if not is_authorized(message):
        bot.reply_to(message, "⛔ У тебя нет доступа к этому боту.")
        return
    bot.reply_to(message, """Привет! 🛡️ Я твой 2FA бот.
Команды:
/add - добавить ключ
/list - выбрать и получить код
/delete - удалить
/reset - удалить всё""")

@bot.message_handler(commands=['add'])
def add(message):
    if not is_authorized(message):
        return
    bot.send_message(message.chat.id, "✍️ Отправь секрет и подпись в одной строке:\n`JBSWY3DPEHPK3PXP GitHub`", parse_mode="Markdown")
    bot.register_next_step_handler(message, process_add)

def process_add(message):
    if not is_authorized(message):
        return
    chat_id = str(message.chat.id)
    parts = message.text.strip().split(" ", 1)
    if len(parts) != 2:
        bot.send_message(message.chat.id, "❌ Формат: `секрет подпись`", parse_mode="Markdown")
        return
    secret, label = parts
    try:
        pyotp.TOTP(secret).now()
    except:
        bot.send_message(message.chat.id, "⚠️ Невалидный секрет.")
        return
    user_data.setdefault(chat_id, []).append({"secret": secret, "label": label})
    save_data()
    bot.send_message(message.chat.id, f"✅ Сохранено как *{label}*", parse_mode="Markdown")

@bot.message_handler(commands=['list'])
def list_keys(message):
    if not is_authorized(message):
        return
    chat_id = str(message.chat.id)
    if not user_data.get(chat_id):
        bot.send_message(message.chat.id, "📭 Нет сохранённых ключей.")
        return
    markup = InlineKeyboardMarkup()
    for idx, entry in enumerate(user_data[chat_id]):
        markup.add(InlineKeyboardButton(entry['label'], callback_data=f"get_{idx}"))
    bot.send_message(message.chat.id, "🔳 Выбери:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("get_"))
def send_code(call):
    if str(call.message.chat.id) != str(ALLOWED_USER_ID):
        return
    chat_id = str(call.message.chat.id)
    index = int(call.data.split("_")[1])
    entry = user_data[chat_id][index]
    code = pyotp.TOTP(entry['secret']).now()
    bot.send_message(call.message.chat.id, f"🔐 *{entry['label']}*: `{code}`", parse_mode="Markdown")

@bot.message_handler(commands=['reset'])
def reset_all(message):
    if not is_authorized(message):
        return
    chat_id = str(message.chat.id)
    user_data[chat_id] = []
    save_data()
    bot.send_message(message.chat.id, "🗑️ Все ключи удалены.")

@bot.message_handler(commands=['delete'])
def delete_key(message):
    if not is_authorized(message):
        return
    chat_id = str(message.chat.id)
    if not user_data.get(chat_id):
        bot.send_message(message.chat.id, "📭 Нет ключей для удаления.")
        return
    markup = InlineKeyboardMarkup()
    for idx, entry in enumerate(user_data[chat_id]):
        markup.add(InlineKeyboardButton(f"❌ {entry['label']}", callback_data=f"del_{idx}"))
    bot.send_message(message.chat.id, "Выбери ключ для удаления:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("del_"))
def confirm_delete(call):
    if str(call.message.chat.id) != str(ALLOWED_USER_ID):
        return
    chat_id = str(call.message.chat.id)
    index = int(call.data.split("_")[1])
    label = user_data[chat_id][index]['label']
    del user_data[chat_id][index]
    save_data()
    bot.send_message(call.message.chat.id, f"🗑️ Ключ *{label}* удалён.", parse_mode="Markdown")

@bot.message_handler(commands=['test'])
def test_bot(message):
    if not is_authorized(message):
        return
    test_secret = "JBSWY3DPEHPK3PXP"
    label = "Тестовый"
    try:
        totp = pyotp.TOTP(test_secret)
        code = totp.now()
        valid = len(code) == 6 and code.isdigit()
        result = "✅ Работает корректно" if valid else "❌ Ошибка генерации кода"
        bot.send_message(message.chat.id, f"""🔍 Тест:
Секрет: `{test_secret}`
Код: `{code}`
Результат: {result}""", parse_mode="Markdown")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Исключение при тесте: {str(e)}")

print("✅ Бот запущен")
bot.infinity_polling()
