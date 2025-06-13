# Contribution Guidelines

Follow these steps when contributing to this project.

## Setup
1. Create a `.env` file based on `.env.example` and set:
   - `TELEGRAM_TOKEN`
   - `ENCRYPTION_KEY`
   - `ALLOWED_USER_IDS`
   See README lines 6-14 for details and `.env.example` lines 1-4 for examples.
2. Install dependencies with `pip install -r requirements.txt`.
3. Run `python bot.py` to make sure the bot works.

## Code style
- Format code using `black`.
- Lint with `flake8`.

## Commit messages
- Write commit messages in English.
- Keep the subject line under 50 characters.

