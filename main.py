from pyrogram import Client
import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

bot = Client("MovieFlix", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def run_bot():
    print("🎬 Movie Flix Telegram Bot Starting...")
    
    # Example admin command
    @bot.on_message(filters.user(OWNER_ID) & filters.command("status"))
    def admin_status(client, message):
        message.reply("✅ Bot is running fine!")

    bot.start()  # Start the bot
    return bot  # Return the client
