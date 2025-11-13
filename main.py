from pyrogram import Client
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Client("MovieFlix", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def run_bot():
    print("🎬 Movie Flix Telegram Bot Starting...")

    # Ensure asyncio loop exists for threaded environments (like Render)
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    bot.run()
    
