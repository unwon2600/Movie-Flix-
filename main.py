from pyrogram import Client
import os

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Client("MovieFlix", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def run_bot():
    print("🎬 Movie Flix Telegram Bot Starting...")
    bot.run()
    
