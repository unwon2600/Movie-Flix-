from pyrogram import Client
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Client("MovieFlix", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def main():
    print("🎬 Movie Flix Telegram Bot Starting...")
    await bot.start()
    print("Bot is running...")
    await bot.idle()  # keeps the bot alive

if __name__ == "__main__":
    asyncio.run(main())
    
