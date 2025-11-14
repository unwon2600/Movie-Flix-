from pyrogram import filters
from main import bot

# --- Example: Auto-filter movies from private messages ---
@bot.on_message(filters.private & filters.text & ~filters.command(["start", "help"]))
async def auto_filter_handler(client, message):
    text = message.text.lower()

    # Simple filter logic: check if "movie" or "film" in message
    if "movie" in text or "film" in text:
        await message.reply("🎬 Movie detected! Processing...")

# --- Example: Auto-filter from channel posts ---
@bot.on_message(filters.channel & filters.text)
async def channel_filter(client, message):
    text = message.text.lower()
    if "movie" in text:
        # Forward to your private channel/group OR do your processing
        await bot.send_message(chat_id=os.getenv("OWNER_ID"), text=f"New movie link detected:\n{text}")
        
