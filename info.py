import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# MongoDB
_raw_mongo = os.getenv("MONGO_URI", "")
# If user provided separate parts, you could build here; but prefer full URI in env
MONGO_URI = _raw_mongo

DATABASE_NAME = os.getenv("DATABASE_NAME", "MovieFlix")
OMDB_API_KEY = os.getenv("OMDB_API_KEY", "")

# parse comma separated values into lists
def _csv_to_int_list(s):
    return [int(x.strip()) for x in s.split(",") if x.strip()]

def _csv_to_ints(s):
    return [int(x.strip()) for x in s.split(",") if x.strip()]

SOURCE_CHAT_IDS = [int(x.strip()) for x in os.getenv("SOURCE_CHAT_IDS", "").split(",") if x.strip()]
ADMINS = [int(x.strip()) for x in os.getenv("ADMINS", "").split(",") if x.strip()]

LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", "0"))
PORT = int(os.getenv("PORT", "8080"))

# default settings (used by DB if no global settings stored)
DEFAULT_SETTINGS = {
    "shortener": False,
    "force_subscribe": False
}
