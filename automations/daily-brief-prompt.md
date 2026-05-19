# Automation Task: Daily Intelligence Brief

Run the local RSS intelligence pipeline and deliver Simran's daily intelligence brief to Telegram.

Requirements:

- Run `.venv/bin/python main.py --send-telegram` from the project root.
- If dependencies are missing, run `.venv/bin/pip install -r requirements.txt` first.
- Keep the total reading time under 10 minutes.
- Avoid clickbait and low-signal repetition.
- Mark each item as `Critical`, `Important`, or `Interesting`.
- Make India and Bhutan coverage substantive.
- Send the generated `daily_brief.md` to Telegram.
- If Telegram credentials are missing, report that `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` need to be configured.
