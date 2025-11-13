from pyrogram import Client, filters
from info import *

bot = Client(
    "AutoFilterBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@bot.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        f"👋 Hello {message.from_user.first_name}!\n\n"
        "I'm an Auto Filter Bot. Send me a movie name or use the channel filter."
    )

print("✅ Bot is starting...")
bot.run()
