#!/bin/bash
# Start Gunicorn server in background
gunicorn backend.app:app &

# Start Telegram bot in foreground
python backend/telegram_bot.py
