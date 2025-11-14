import asyncio
import glob
import importlib
import logging
from pathlib import Path

from pyrogram import Client, idle
from info import API_ID, API_HASH, BOT_TOKEN

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# create the bot client
app = Client(
    "movieflix_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ensure plugins package exists (create __init__ if not present locally)
# Load plugins AFTER app created so plugins can import `from main import app`
for path in glob.glob("plugins/*.py"):
    name = Path(path).stem
    # skip __init__ if present
    if name == "__init__":
        continue
    try:
        importlib.import_module(f"plugins.{name}")
        logging.info(f"Loaded plugin: {name}")
    except Exception as e:
        logging.exception(f"Failed to load plugin {name}: {e}")

async def main():
    await app.start()
    logging.info("🎬 Movie Flix Filter Bot started.")
    await idle()
    await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
