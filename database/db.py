import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from info import MONGO_URI, DATABASE_NAME, DEFAULT_SETTINGS
from bson import ObjectId

if not MONGO_URI:
    raise RuntimeError("MONGO_URI is not set. Please define it in environment variables.")

client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]

files_col = db.get_collection("files")
settings_col = db.get_collection("settings")
users_col = db.get_collection("users")

async def ensure_settings():
    doc = await settings_col.find_one({"_id": "global"})
    if not doc:
        await settings_col.insert_one({"_id": "global", **DEFAULT_SETTINGS})

# Run ensure_settings in background
loop = asyncio.get_event_loop()
loop.create_task(ensure_settings())

# File helpers
async def add_file(item: dict):
    """Insert item if that message isn't already indexed."""
    chat_id = item.get("chat_id")
    message_id = item.get("message_id")
    if chat_id and message_id:
        exists = await files_col.find_one({"chat_id": chat_id, "message_id": message_id})
        if exists:
            return False
    res = await files_col.insert_one(item)
    return True if res.inserted_id else False

async def search_files(query: str, limit: int = 50):
    cursor = files_col.find({"title": {"$regex": query, "$options": "i"}}).limit(limit)
    return [doc async for doc in cursor]

async def get_all_files_for_title(title: str):
    cursor = files_col.find({"title": {"$regex": f"^{title}$", "$options": "i"}})
    return [doc async for doc in cursor]

# Settings helpers
async def get_settings():
    doc = await settings_col.find_one({"_id": "global"})
    if not doc:
        await ensure_settings()
        doc = await settings_col.find_one({"_id": "global"})
    return doc

async def set_setting(key: str, value):
    await settings_col.update_one({"_id": "global"}, {"$set": {key: value}}, upsert=True)
    return await get_settings()
