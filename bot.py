from dotenv import load_dotenv
import os
import telebot
import pyotp
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from auth import (
    load_auth_users,
    authorize_user,
    revoke_user,
    is_authorized,
)

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN is not set")

bot = telebot.TeleBot(TOKEN)

# In-memory storage for TOTP secrets per user
user_secrets = {}

# Load authorized users at startup
load_auth_users()

def require_auth(func):
    def wrapper(message, *args, **kwargs):
        if not is_authorized(message.from_user.id):
            bot.reply_to(message, "\u26d4\ufe0f Access denied. Use /auth first.")
            return
        return func(message, *args, **kwargs)
    return wrapper

@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "\u2705 Telegram TOTP Bot. Use /auth to authorize your Telegram ID.",
    )

@bot.message_handler(commands=["auth"])
def auth_user(message):
    user_id = message.from_user.id
    if is_authorized(user_id):
        bot.reply_to(message, "\u2705 Already authorized.")
    else:
        authorize_user(user_id)
        bot.reply_to(message, "\u2705 Authorization successful.")

@bot.message_handler(commands=["add"])
@require_auth
def add(message):
    bot.send_message(
        message.chat.id,
        "Send secret and label on one line:\n`JBSWY3DPEHPK3PXP GitHub`",
        parse_mode="Markdown",
    )
    bot.register_next_step_handler(message, process_add)

def process_add(message):
    if not is_authorized(message.from_user.id):
        return
    parts = message.text.strip().split(" ", 1)
    if len(parts) != 2:
        bot.send_message(
            message.chat.id,
            "Format: `secret label`",
            parse_mode="Markdown",
        )
        return
    secret, label = parts
    try:
        pyotp.TOTP(secret).now()
    except Exception:
        bot.send_message(message.chat.id, "Invalid secret.")
        return
    user_secrets.setdefault(message.from_user.id, []).append({"secret": secret, "label": label})
    bot.send_message(message.chat.id, f"\u2705 Saved as *{label}*", parse_mode="Markdown")

@bot.message_handler(commands=["list"])
@require_auth
def list_keys(message):
    secrets = user_secrets.get(message.from_user.id)
    if not secrets:
        bot.send_message(message.chat.id, "\u2139\ufe0f No secrets added.")
        return
    markup = InlineKeyboardMarkup()
    for idx, entry in enumerate(secrets):
        markup.add(InlineKeyboardButton(entry["label"], callback_data=f"get_{idx}"))
    bot.send_message(message.chat.id, "Choose:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("get_"))
def send_code(call):
    if not is_authorized(call.from_user.id):
        return
    idx = int(call.data.split("_")[1])
    entry = user_secrets.get(call.from_user.id, [])[idx]
    code = pyotp.TOTP(entry["secret"]).now()
    bot.send_message(call.message.chat.id, f"*{entry['label']}*: `{code}`", parse_mode="Markdown")

@bot.message_handler(commands=["delete"])
@require_auth
def delete_key(message):
    secrets = user_secrets.get(message.from_user.id)
    if not secrets:
        bot.send_message(message.chat.id, "\u2139\ufe0f Nothing to delete.")
        return
    markup = InlineKeyboardMarkup()
    for idx, entry in enumerate(secrets):
        markup.add(InlineKeyboardButton(f"\u274c {entry['label']}", callback_data=f"del_{idx}"))
    bot.send_message(message.chat.id, "Choose secret to delete:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("del_"))
def confirm_delete(call):
    if not is_authorized(call.from_user.id):
        return
    idx = int(call.data.split("_")[1])
    secrets = user_secrets.get(call.from_user.id)
    if secrets and 0 <= idx < len(secrets):
        label = secrets[idx]["label"]
        del secrets[idx]
        bot.send_message(call.message.chat.id, f"Deleted *{label}*", parse_mode="Markdown")

@bot.message_handler(commands=["reset"])
@require_auth
def reset_all(message):
    user_secrets[message.from_user.id] = []
    bot.send_message(message.chat.id, "All secrets removed.")

print("Bot started")
bot.infinity_polling()
