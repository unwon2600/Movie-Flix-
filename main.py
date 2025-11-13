from pyrogram import Client, errors
import time
import os

# Load environment variables (if you use dotenv)
from dotenv import load_dotenv
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Client(
    "MovieFlixBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

print("✅ Bot is starting...")

while True:
    try:
        bot.run()
    except errors.FloodWait as e:
        wait_time = e.value
        print(f"⚠️ FloodWait detected! Waiting for {wait_time} seconds...")
        time.sleep(wait_time + 5)
        continue
    except Exception as err:
        print(f"❌ Unexpected error: {err}")
        print("🔁 Restarting in 10 seconds...")
        time.sleep(10)
        continue
