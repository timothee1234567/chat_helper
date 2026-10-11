"""
A minimal Telegram webhook server, built for $0 hosting.

Render's free web services sleep after 15 minutes of no traffic and wake
up when an HTTP request arrives. Telethon's style (telegram_bot.py) keeps
a connection open permanently, which doesn't fit a service that sleeps.
This version flips the model: Telegram POSTs new messages to us, which is
exactly the kind of request that wakes a sleeping free service back up.

Bonus: this only needs a BOT_TOKEN from @BotFather. The API_ID/API_HASH
from my.telegram.org (used in telegram_bot.py) are not needed here at all
— those are for Telethon's user-account-style client, which this doesn't
use.

Needs: pip install flask requests
"""

import json
import os

import requests
from flask import Flask, request

from brain import get_reply
from llm_client import real_llm

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "your_bot_token_here")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

with open("business.json", "r", encoding="utf-8") as f:
    business = json.load(f)

app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json(silent=True) or {}
    message = update.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text")

    if chat_id and text:
        reply = get_reply(text, business, real_llm)
        requests.post(
            f"{TELEGRAM_API}/sendMessage",
            json={"chat_id": chat_id, "text": reply},
            timeout=10,
        )

    return "ok"


@app.route("/")
def home():
    # Render (or you) can hit this to confirm the service is alive.
    return "Bot is running."


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
