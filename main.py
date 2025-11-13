# main.py
from pyrogram import Client
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Create the client but do NOT call run() here
bot = Client("MovieFlix", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Example handlers (keep/extend as needed)
from pyrogram import filters
@bot.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    await message.reply_text(f"👋 Hello {message.from_user.first_name}! Movie Flix Auto Filter Bot is online.")

# Owner commands example (make sure OWNER_ID env var set)
OWNER_ID = os.getenv("OWNER_ID")
if OWNER_ID:
    try:
        OWNER_ID = int(OWNER_ID)
    except:
        OWNER_ID = None

@bot.on_message(filters.command("restart") & filters.user(OWNER_ID))
async def restart_cmd(client, message):
    await message.reply_text("♻️ Restarting...")
    # This will crash the process so Render restarts it
    import os, time
    time.sleep(1)
    os.kill(1, 9)

def run_bot():
    """
    Start the bot in the current thread's asyncio loop and return the Client instance.
    This function is safe to call from a fresh event loop created in a separate thread.
    """
    print("🎬 Movie Flix Telegram Bot Starting...")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # start the bot and return it (bot.start() is a coroutine)
    loop.run_until_complete(bot.start())
    print("✅ Bot started successfully!")
    return bot
    
