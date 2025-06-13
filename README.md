# telegram-totp-secure

Telegram bot for generating TOTP codes with simple authorization.

## Features

- Authorization by Telegram ID via `/auth`
- Store TOTP secrets in RAM only
- Authorized IDs saved in encrypted `auth_users.enc`
- Commands: `/start`, `/auth`, `/add`, `/list`, `/delete`, `/reset`

## Setup

1. Copy `.env.example` to `.env` and fill in values.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the bot:
   ```bash
   python bot.py
   ```

## Versioning

Current version: **v1.0.0**
