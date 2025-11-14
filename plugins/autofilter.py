from pyrogram import Client, filters
from main import bot  # Import the main bot Client instance

# Example handler for private messages
@bot.on_message(filters.private & filters.text & ~filters.command(["start", "help"]))
async def auto_filter_handler(client, message):
    text = message.text.lower()
    if "movie" in text:  # Replace this with your actual filter logic
        await message.reply("🎬 Movie detected! Processing...")
        
