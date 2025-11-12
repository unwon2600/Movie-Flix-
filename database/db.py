from motor.motor_asyncio import AsyncIOMotorClient
from info import MONGO_URI, DEFAULT_SETTINGS
import asyncio

client = AsyncIOMotorClient(MONGO_URI)
db = client.movieflix

# Collections
files_col = db.files            # stores files: title, year, language, quality, file_id, chat_id, message_id, imdb_id, poster
settings_col = db.settings      # stores toggles like shortener, force_subscribe
users_col = db.users            # optional user metadata

# init default settings if not present
async def ensure_settings():
    doc = await settings_col.find_one({"_id": "global"})
    if not doc:
        await settings_col.insert_one({"_id": "global", **DEFAULT_SETTINGS})

# file helpers
async def add_file(item):
    """
    item: dict with keys: title, year, language, quality, file_id, chat_id, message_id, imdb_id, poster
    """
    q = {
        "title": item.get("title"),
        "language": item.get("language"),
        "quality": item.get("quality"),
        "file_id": item.get("file_id"),
        "chat_id": item.get("chat_id"),
        "message_id": item.get("message_id"),
        "imdb_id": item.get("imdb_id"),
    }
    # avoid duplicate for same message
    exists = await files_col.find_one({"chat_id": q["chat_id"], "message_id": q["message_id"]})
    if not exists:
        await files_col.insert_one({**item})
        return True
    return False

async def search_files(query, limit=20):
    """Case-insensitive regex search on title"""
    cursor = files_col.find({"title": {"$regex": query, "$options": "i"}}).limit(limit)
    return [doc async for doc in cursor]

async def get_all_files_for_title(title):
    cursor = files_col.find({"title": {"$regex": f"^{title}$", "$options": "i"}})
    return [doc async for doc in cursor]

# settings helpers
async def get_settings():
    doc = await settings_col.find_one({"_id": "global"})
    if not doc:
        await ensure_settings()
        doc = await settings_col.find_one({"_id": "global"})
    return doc

async def set_setting(key, value):
    await settings_col.update_one({"_id": "global"}, {"$set": {key: value}}, upsert=True)
    return await get_settings()

# run ensure on import loop
loop = asyncio.get_event_loop()
loop.create_task(ensure_settings())
