import os
from dotenv import load_dotenv

# load .env file
load_dotenv()

API_ID = int(os.getenv("21930652"))
API_HASH = os.getenv("6cf4623177849a4e534963d98446792e")
BOT_TOKEN = os.getenv("7852466875:AAHKWS6s0JVAReFLo6YoFSmKk-hXtds0u0Y")
MONGO_URI = os.getenv("mongodb+srv://unwon2600_db_user:<@unwonperson2600>@unwon.fgh9aoq.mongodb.net/?appName=unwon")
OWNER_ID = int(os.getenv("-7310926033"))
LOG_CHANNEL = int(os.getenv("-1002579386518"))
FILE_CHANNEL = int(os.getenv("-1002676537585"))
