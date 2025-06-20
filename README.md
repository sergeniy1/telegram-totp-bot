# Telegram TOTP Bot

This bot stores TOTP secrets and returns one-time codes on demand. Secrets
are encrypted using `cryptography` and stored in `totp_data.json`.

## Configuration
Create a `.env` file based on `.env.example` and set:

- `TELEGRAM_TOKEN` – bot token from [BotFather](https://t.me/BotFather)
- `ENCRYPTION_KEY` – key for `Fernet` encryption (use `python -m cryptography.fernet` to generate)
- `ALLOWED_USER_IDS` – comma-separated list of Telegram user IDs allowed to interact with the bot

The `totp_data.json` file is encrypted and ignored by git.

## Running the bot
Install dependencies and start the bot:

```bash
pip install -r requirements.txt
python bot.py
```

---

## \u041f\u043e-\u0440\u0443\u0441\u0441\u043a\u0438

\u042d\u0442\u043e\u0442 \u0431\u043e\u0442 \u0445\u0440\u0430\u043d\u0438\u0442 TOTP \u0441\u0435\u043a\u0440\u0435\u0442\u044b \u0438 \u0432\u044b\u0434\u0430\u0451\u0442 \u043e\u0434\u043d\u043e\u0440\u0430\u0437\u043e\u0432\u044b\u0435 \u043a\u043e\u0434\u044b \u043f\u043e \u0437\u0430\u043f\u0440\u043e\u0441\u0443. \u0421\u0435\u043a\u0440\u0435\u0442\u044b \u0437\u0430\u0448\u0438\u0444\u0440\u043e\u0432\u0430\u043d\u044b \u043f\u0440\u0438 \u043f\u043e\u043c\u043e\u0449\u0438 `cryptography` \u0438 \u0445\u0440\u0430\u043d\u044f\u0442\u0441\u044f \u0432 `totp_data.json`.

### \u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430
\u0421\u043e\u0437\u0434\u0430\u0439\u0442\u0435 \u0444\u0430\u0439\u043b `.env` \u043d\u0430 \u043e\u0441\u043d\u043e\u0432\u0435 `.env.example` \u0438 \u0443\u043a\u0430\u0436\u0438\u0442\u0435:

- `TELEGRAM_TOKEN` \u2014 \u0442\u043e\u043a\u0435\u043d \u0431\u043e\u0442\u0430 \u043e\u0442 [BotFather](https://t.me/BotFather)
- `ENCRYPTION_KEY` \u2014 \u043a\u043b\u044e\u0447 `Fernet` (\u0441\u0433\u0435\u043d\u0435\u0440\u0438\u0440\u0443\u0439\u0442\u0435 \u043a\u043e\u043c\u0430\u043d\u0434\u043e\u0439 `python -m cryptography.fernet`)
- `ALLOWED_USER_IDS` \u2014 \u0441\u043f\u0438\u0441\u043e\u043a ID Telegram \u0447\u0435\u0440\u0435\u0437 \u0437\u0430\u043f\u044f\u0442\u0443, \u043a\u043e\u0442\u043e\u0440\u044b\u043c \u0440\u0430\u0437\u0440\u0435\u0448\u0451\u043d \u0434\u043e\u0441\u0442\u0443\u043f \u043a \u0431\u043e\u0442\u0443

`totp_data.json` \u0437\u0430\u0448\u0438\u0444\u0440\u043e\u0432\u0430\u043d \u0438 \u0438\u0433\u043d\u043e\u0440\u0438\u0440\u0443\u0435\u0442\u0441\u044f git.

### \u0417\u0430\u043f\u0443\u0441\u043a \u0431\u043e\u0442\u0430
\u0423\u0441\u0442\u0430\u043d\u043e\u0432\u0438\u0442\u0435 \u0437\u0430\u0432\u0438\u0441\u0438\u043c\u043e\u0441\u0442\u0438 \u0438 \u0437\u0430\u043f\u0443\u0441\u0442\u0438\u0442\u0435:

```bash
pip install -r requirements.txt
python bot.py
```

