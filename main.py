from pyrogram import Client
import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Create the bot client
bot = Client(
    "MovieFlix",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

def run_bot():
    """
    Start the bot in non-blocking mode and return the Client instance.
    """
    print("🎬 Movie Flix Telegram Bot Starting...")
    bot.start()
    return bot
    
