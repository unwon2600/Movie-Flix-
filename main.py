import asyncio
import logging
import glob
import importlib
from pathlib import Path

from pyrogram import Client, idle
from info import *

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = Client("movieflix", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# auto-load plugins from plugins/ directory
for path in glob.glob("plugins/*.py"):
    name = Path(path).stem
    importlib.import_module(f"plugins.{name}")
    logging.info(f"Loaded plugin: {name}")

async def main():
    await app.start()
    logging.info("🎬 Movie Flix Filter Bot started.")
    # optionally, you can send a startup message to LOG_CHANNEL if configured
    if LOG_CHANNEL:
        try:
            await app.send_message(LOG_CHANNEL, "Movie Flix Filter Bot started ✅")
        except Exception as e:
            logging.warning("Couldn't send startup message to LOG_CHANNEL: %s", e)
    await idle()
    await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
