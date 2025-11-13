from info import *
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

app = Client(
    "AutoFilterBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    name = message.from_user.first_name
    buttons = [
        [InlineKeyboardButton("📢 Channel", url="https://t.me/YourChannel")],
        [InlineKeyboardButton("👤 Owner", url="https://t.me/YourOwner")]
    ]
    await message.reply_text(
        f"Hello {name} 👋\n\nI am your Auto Filter Movie Bot!",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

app.run()
