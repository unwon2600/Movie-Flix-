import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
MONGO_URI = os.getenv("MONGO_URI", "")
LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", "0"))

# parse comma separated
SOURCE_CHAT_IDS = [int(x.strip()) for x in os.getenv("SOURCE_CHAT_IDS", "").split(",") if x.strip()]
ADMINS = [int(x.strip()) for x in os.getenv("ADMINS", "").split(",") if x.strip()]

PORT = int(os.getenv("PORT", "8080"))

# Default toggles (can be updated via admin commands & saved in DB)
DEFAULT_SETTINGS = {
    "shortener": False,
    "force_subscribe": False
}
