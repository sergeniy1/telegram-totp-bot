from dotenv import load_dotenv
import os
import telebot
import pyotp
import json
from cryptography.fernet import Fernet
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# \u0417\u0430\u0433\u0440\u0443\u0436\u0430\u0435\u043c \u043f\u0435\u0440\u0435\u043c\u0435\u043d\u043d\u044b\u0435 \u0438\u0437 .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
ALLOWED_USER_IDS = [
    uid.strip() for uid in os.getenv("ALLOWED_USER_IDS", "").split(",") if uid.strip()
]
if not TOKEN:
    raise Exception("\u274c \u0412 .env \u0434\u043e\u043b\u0436\u0435\u043d \u0431\u044b\u0442\u044c TELEGRAM_TOKEN")
if not ALLOWED_USER_IDS:
    raise Exception(
        "\u274c \u0412 .env \u0434\u043e\u043b\u0436\u0435\u043d \u0431\u044b\u0442\u044c ALLOWED_USER_IDS"
    )
DATA_FILE = "totp_data.json"

if not ENCRYPTION_KEY:
    raise Exception("\u274c \u0412 .env \u0434\u043e\u043b\u0436\u0435\u043d \u0431\u044b\u0442\u044c ENCRYPTION_KEY")

fernet = Fernet(ENCRYPTION_KEY.encode())
bot = telebot.TeleBot(TOKEN)

# \u0417\u0430\u0433\u0440\u0443\u0437\u043a\u0430 \u0438 \u0440\u0430\u0441\u0448\u0438\u0444\u0440\u043e\u0432\u043a\u0430 \u0441\u043e\u0445\u0440\u0430\u043d\u0451\u043d\u043d\u044b\u0445 \u0434\u0430\u043d\u043d\u044b\u0445
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "rb") as f:
        try:
            user_data = json.loads(fernet.decrypt(f.read()))
        except:
            user_data = {}
else:
    user_data = {}

# \u0421\u043e\u0445\u0440\u0430\u043d\u044f\u0435\u043c \u0437\u0430\u0448\u0438\u0444\u0440\u043e\u0432\u0430\u043d\u043d\u044b\u0435 \u0434\u0430\u043d\u043d\u044b\u0435 \u0432 \u0444\u0430\u0439\u043b

def save_data():
    with open(DATA_FILE, "wb") as f:
        f.write(fernet.encrypt(json.dumps(user_data).encode()))

# \u041f\u0440\u043e\u0432\u0435\u0440\u043a\u0430 \u0430\u0432\u0442\u043e\u0440\u0438\u0437\u0430\u0446\u0438\u0438 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f

def is_authorized(message):
    return str(message.chat.id) in ALLOWED_USER_IDS

@bot.message_handler(commands=['start'])
def start(message):
    if not is_authorized(message):
        bot.reply_to(message, "\u26d4 \u0423 \u0442\u0435\u0431\u044f \u043d\u0435\u0442 \u0434\u043e\u0441\u0442\u0443\u043f\u0430 \u043a \u044d\u0442\u043e\u043c\u0443 \u0431\u043e\u0442\u0443.")
        return
    bot.reply_to(message, """\u041f\u0440\u0438\u0432\u0435\u0442! \ud83d\udea1\ufe0f \u042f \u0442\u0432\u043e\u0439 2FA \u0431\u043e\u0442.
\u041a\u043e\u043c\u0430\u043d\u0434\u044b:
/add - \u0434\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u043a\u043b\u044e\u0447
/list - \u0432\u044b\u0431\u0440\u0430\u0442\u044c \u0438 \u043f\u043e\u043b\u0443\u0447\u0438\u0442\u044c \u043a\u043e\u0434
/delete - \u0443\u0434\u0430\u043b\u0438\u0442\u044c
/reset - \u0443\u0434\u0430\u043b\u0438\u0442\u044c \u0432\u0441\u0451""")

@bot.message_handler(commands=['add'])
def add(message):
    if not is_authorized(message):
        return
    bot.send_message(message.chat.id, "\u270d\ufe0f \u041e\u0442\u043f\u0440\u0430\u0432\u044c \u0441\u0435\u043a\u0440\u0435\u0442 \u0438 \u043f\u043e\u0434\u043f\u0438\u0441\u044c \u0432 \u043e\u0434\u043d\u043e\u0439 \u0441\u0442\u0440\u043e\u043a\u0435:\n`JBSWY3DPEHPK3PXP GitHub`", parse_mode="Markdown")
    bot.register_next_step_handler(message, process_add)

def process_add(message):
    if not is_authorized(message):
        return
    chat_id = str(message.chat.id)
    parts = message.text.strip().split(" ", 1)
    if len(parts) != 2:
        bot.send_message(message.chat.id, "\u274c \u0424\u043e\u0440\u043c\u0430\u0442: `\u0441\u0435\u043a\u0440\u0435\u0442 \u043f\u043e\u0434\u043f\u0438\u0441\u044c`", parse_mode="Markdown")
        return
    secret, label = parts
    try:
        pyotp.TOTP(secret).now()
    except:
        bot.send_message(message.chat.id, "\u26a0\ufe0f \u041d\u0435\u0432\u0430\u043b\u0438\u0434\u043d\u044b\u0439 \u0441\u0435\u043a\u0440\u0435\u0442.")
        return
    user_data.setdefault(chat_id, []).append({"secret": secret, "label": label})
    save_data()
    bot.send_message(message.chat.id, f"\u2705 \u0421\u043e\u0445\u0440\u0430\u043d\u0435\u043d\u043e \u043a\u0430\u043a *{label}*", parse_mode="Markdown")

@bot.message_handler(commands=['list'])
def list_keys(message):
    if not is_authorized(message):
        return
    chat_id = str(message.chat.id)
    if not user_data.get(chat_id):
        bot.send_message(message.chat.id, "\ud83d\udcec \u041d\u0435\u0442 \u0441\u043e\u0445\u0440\u0430\u043d\u0451\u043d\u043d\u044b\u0445 \u043a\u043b\u044e\u0447\u0435\u0439.")
        return
    markup = InlineKeyboardMarkup()
    for idx, entry in enumerate(user_data[chat_id]):
        markup.add(InlineKeyboardButton(entry['label'], callback_data=f"get_{idx}"))
    bot.send_message(message.chat.id, "\ud83d\udd33 \u0412\u044b\u0431\u0435\u0440\u0438:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("get_"))
def send_code(call):
    if str(call.message.chat.id) not in ALLOWED_USER_IDS:
        return
    chat_id = str(call.message.chat.id)
    index = int(call.data.split("_")[1])
    entry = user_data[chat_id][index]
    code = pyotp.TOTP(entry['secret']).now()
    bot.send_message(call.message.chat.id, f"\ud83d\udd10 *{entry['label']}*: `{code}`", parse_mode="Markdown")

@bot.message_handler(commands=['reset'])
def reset_all(message):
    if not is_authorized(message):
        return
    chat_id = str(message.chat.id)
    user_data[chat_id] = []
    save_data()
    bot.send_message(message.chat.id, "\ud83d\uddd1\ufe0f \u0412\u0441\u0435 \u043a\u043b\u044e\u0447\u0438 \u0443\u0434\u0430\u043b\u0435\u043d\u044b.")

@bot.message_handler(commands=['delete'])
def delete_key(message):
    if not is_authorized(message):
        return
    chat_id = str(message.chat.id)
    if not user_data.get(chat_id):
        bot.send_message(message.chat.id, "\ud83d\udcec \u041d\u0435\u0442 \u043a\u043b\u044e\u0447\u0435\u0439 \u0434\u043b\u044f \u0443\u0434\u0430\u043b\u0435\u043d\u0438\u044f.")
        return
    markup = InlineKeyboardMarkup()
    for idx, entry in enumerate(user_data[chat_id]):
        markup.add(InlineKeyboardButton(f"\u274c {entry['label']}", callback_data=f"del_{idx}"))
    bot.send_message(message.chat.id, "\u0412\u044b\u0431\u0435\u0440\u0438 \u043a\u043b\u044e\u0447 \u0434\u043b\u044f \u0443\u0434\u0430\u043b\u0435\u043d\u0438\u044f:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("del_"))
def confirm_delete(call):
    if str(call.message.chat.id) not in ALLOWED_USER_IDS:
        return
    chat_id = str(call.message.chat.id)
    index = int(call.data.split("_")[1])
    label = user_data[chat_id][index]['label']
    del user_data[chat_id][index]
    save_data()
    bot.send_message(call.message.chat.id, f"\ud83d\uddd1\ufe0f \u041a\u043b\u044e\u0447 *{label}* \u0443\u0434\u0430\u043b\u0451\u043d.", parse_mode="Markdown")

@bot.message_handler(commands=['test'])
def test_bot(message):
    if not is_authorized(message):
        return
    test_secret = "JBSWY3DPEHPK3PXP"
    label = "\u0422\u0435\u0441\u0442\u043e\u0432\u044b\u0439"
    try:
        totp = pyotp.TOTP(test_secret)
        code = totp.now()
        valid = len(code) == 6 and code.isdigit()
        result = "\u2705 \u0420\u0430\u0431\u043e\u0442\u0430\u0435\u0442 \u043a\u043e\u0440\u0440\u0435\u043a\u0442\u043d\u043e" if valid else "\u274c \u041e\u0448\u0438\u0431\u043a\u0430 \u0433\u0435\u043d\u0435\u0440\u0430\u0446\u0438\u0438 \u043a\u043e\u0434\u0430"
        bot.send_message(message.chat.id, f"""\ud83d\udd0d \u0422\u0435\u0441\u0442:
\u0421\u0435\u043a\u0440\u0435\u0442: `{test_secret}`
\u041a\u043e\u0434: `{code}`
\u0420\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442: {result}""", parse_mode="Markdown")
    except Exception as e:
        bot.send_message(message.chat.id, f"\u274c \u0418\u0441\u043a\u043b\u044e\u0447\u0435\u043d\u0438\u0435 \u043f\u0440\u0438 \u0442\u0435\u0441\u0442\u0435: {str(e)}")

print("\u2705 \u0411\u043e\u0442 \u0437\u0430\u043f\u0443\u0449\u0435\u043d")
bot.infinity_polling()
