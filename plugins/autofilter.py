import asyncio
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import Client
from imdb import Cinemagoer
from rapidfuzz import process, fuzz
import requests

from main import app
from info import SOURCE_CHAT_IDS, ADMINS, LOG_CHANNEL
from database.db import add_file, search_files, get_all_files_for_title, get_settings, set_setting, files_col
from database.db import client as mongo_client
from pyrogram.errors import RPCError

ia = Cinemagoer()

# ---------- Helpers ----------
async def fetch_imdb_by_title(title):
    # Cinemagoer is sync — run in executor
    loop = asyncio.get_event_loop()
    results = await loop.run_in_executor(None, ia.search_movie, title)
    if not results:
        return None
    movie = results[0]
    movie_full = await loop.run_in_executor(None, ia.get_movie, movie.movieID)
    return movie_full

def shorten_url(url):
    # tinyurl simple API
    try:
        r = requests.get("https://tinyurl.com/api-create.php", params={"url": url}, timeout=6)
        if r.status_code == 200:
            return r.text
    except:
        pass
    return url

async def is_user_subscribed(user_id, app_client):
    """
    placeholder force-subscribe check.
    If force_subscribe is on, you should check membership in a CHANNEL (AUTH_CHANNEL) — not implemented here.
    """
    settings = await get_settings()
    if not settings.get("force_subscribe", False):
        return True
    # Implement actual check against an AUTH channel if you have one (AUTH_CHANNEL in info.py)
    return True

# ---------- Auto-index incoming files from source chats ----------
@Client.on_message(app, filters.chat(SOURCE_CHAT_IDS) & (filters.document | filters.video | filters.audio | filters.photo))
async def index_incoming_file(client, message):
    title_guess = None
    if message.document:
        title_guess = message.document.file_name
        file_id = message.document.file_id
    elif message.video:
        title_guess = getattr(message.video, "file_name", None) or message.caption or "video"
        file_id = message.video.file_id
    elif message.audio:
        title_guess = getattr(message.audio, "file_name", None) or message.caption or "audio"
        file_id = message.audio.file_id
    elif message.photo:
        title_guess = message.caption or "photo"
        file_id = message.photo.file_id

    # simple clean title: take until first '.' or '[' if exists
    clean_title = title_guess.split('[')[0].split('(')[0].split('.')[0].strip()
    # try fetch imdb to get imdb id & poster
    imdb_id = None
    poster = None
    year = None
    try:
        movie = await fetch_imdb_by_title(clean_title)
        if movie:
            imdb_id = movie.movieID
            poster = movie.get('cover url')
            year = movie.get('year')
    except Exception:
        pass

    item = {
        "title": clean_title,
        "year": year,
        "language": "Unknown",
        "quality": "Unknown",
        "file_id": file_id,
        "chat_id": message.chat.id,
        "message_id": message.message_id,
        "imdb_id": imdb_id,
        "poster": poster
    }
    saved = await add_file(item)
    if saved:
        try:
            await client.send_message(LOG_CHANNEL, f"Indexed: {clean_title} from {message.chat.id}")
        except Exception:
            pass

# ---------- Direct text search handler (non-command) ----------
@Client.on_message(app, filters.text & ~filters.private & ~filters.command)
async def ignore_group_texts(client, message):
    # ignore group chats not required — we want private queries + maybe groups; adjust as needed
    return

@Client.on_message(app, filters.private & filters.text & ~filters.command)
async def direct_search(client, message):
    query = message.text.strip()
    if not query:
        return

    # Force-subscribe check (placeholder)
    ok = await is_user_subscribed(message.from_user.id, client)
    if not ok:
        return await message.reply_text("Please subscribe to the required channel to use the bot.")

    # 1) search DB first
    results = await search_files(query, limit=50)
    if results:
        # prepare IMDB metadata from first matched title (best guess)
        first = results[0]
        imdb_id = first.get("imdb_id")
        imdb_data = None
        if imdb_id:
            loop = asyncio.get_event_loop()
            try:
                imdb_data = await loop.run_in_executor(None, ia.get_movie, imdb_id)
            except Exception:
                imdb_data = None

        caption = f"🔎 Results for **{query}**\n\n"
        if imdb_data:
            title = imdb_data.get('title')
            year = imdb_data.get('year', '')
            rating = imdb_data.get('rating', 'N/A')
            plot = (imdb_data.get('plot outline') or '')
            caption = f"🎬 **{title} ({year})**\n⭐ IMDb: {rating}\n\n{plot}\n\nAvailable Files:\n"

        # create dynamic buttons grouped by language/quality
        buttons = []
        for doc in results[:25]:
            label = f"{doc.get('language','Unknown')} {doc.get('quality','Unknown')}"
            cb = f"getfile|{str(doc.get('_id'))}"
            buttons.append([InlineKeyboardButton(label, callback_data=cb)])

        # add Send All & other control buttons
        buttons.append([InlineKeyboardButton("Send All 🎞️", callback_data=f"sendall|{query}")])
        buttons.append([InlineKeyboardButton("More Info (IMDb)", callback_data=f"imdb|{imdb_id or ''}")])

        # send poster if exists
        poster = first.get("poster")
        try:
            if poster:
                await client.send_photo(message.chat.id, poster, caption=caption, reply_markup=InlineKeyboardMarkup(buttons))
            else:
                await client.send_message(message.chat.id, caption, reply_markup=InlineKeyboardMarkup(buttons))
        except Exception as e:
            await client.send_message(message.chat.id, caption, reply_markup=InlineKeyboardMarkup(buttons))
        return

    # 2) If DB empty, fallback to IMDb search + suggestion (spell-check)
    loop = asyncio.get_event_loop()
    try:
        imdb_results = await loop.run_in_executor(None, ia.search_movie, query)
    except Exception:
        imdb_results = []

    if not imdb_results:
        return await message.reply_text("Kono result pawa jayni. Spelling check kore dekho or try another name.")

    best = imdb_results[0]
    # get details
    movie_full = await loop.run_in_executor(None, ia.get_movie, best.movieID)
    title = movie_full.get('title')
    year = movie_full.get('year', '')
    rating = movie_full.get('rating', 'N/A')
    plot = (movie_full.get('plot outline') or '')
    poster = movie_full.get('cover url')
    caption = f"🎬 **{title} ({year})**\n⭐ IMDb: {rating}\n\n{plot}\n\nNo files found in database. If you have these files, add them to the source group to index."

    kb = [
        [InlineKeyboardButton("Search IMDb ▶️", callback_data=f"imdb|{movie_full.movieID}")],
    ]
    if poster:
        await client.send_photo(message.chat.id, poster, caption=caption, reply_markup=InlineKeyboardMarkup(kb))
    else:
        await client.send_message(message.chat.id, caption, reply_markup=InlineKeyboardMarkup(kb))

# ---------- Callback Query Handlers ----------
@Client.on_callback_query(app)
async def cb_handler(client, callback_query):
    data = callback_query.data or ""
    user = callback_query.from_user
    if data.startswith("getfile|"):
        _id = data.split("|",1)[1]
        # fetch doc by _id
        from bson import ObjectId
        try:
            doc = await files_col.find_one({"_id": ObjectId(_id)})
        except Exception:
            doc = None
        if not doc:
            return await callback_query.answer("File not found.", show_alert=True)
        # send file (copy message from original chat)
        try:
            await client.copy_message(chat_id=callback_query.message.chat.id,
                                      from_chat_id=doc["chat_id"],
                                      message_id=doc["message_id"])
            await callback_query.answer("Sending file...")
        except RPCError as e:
            await callback_query.answer("Failed to send file. Bot may not have access.", show_alert=True)

    elif data.startswith("sendall|"):
        query = data.split("|",1)[1]
        await callback_query.answer("Sending all matches... This may take some time.")
        matches = await search_files(query, limit=200)
        sent = 0
        for doc in matches:
            try:
                await client.copy_message(chat_id=callback_query.message.chat.id,
                                          from_chat_id=doc["chat_id"],
                                          message_id=doc["message_id"])
                sent += 1
                await asyncio.sleep(0.3)
            except Exception:
                continue
        await callback_query.message.reply_text(f"Sent {sent} files for '{query}'")
    elif data.startswith("imdb|"):
        imdb_id = data.split("|",1)[1]
        if not imdb_id:
            return await callback_query.answer("No IMDb ID available.", show_alert=True)
        loop = asyncio.get_event_loop()
        try:
            movie = await loop.run_in_executor(None, ia.get_movie, imdb_id)
        except Exception:
            return await callback_query.answer("Failed to fetch IMDb data.", show_alert=True)
        text = f"🎬 {movie.get('title')} ({movie.get('year','')})\n⭐ IMDb: {movie.get('rating','N/A')}\n\n{movie.get('plot outline','')}"
        await callback_query.message.reply_text(text)
    else:
        await callback_query.answer()
        ModuleNotFoundError: No module named 'requests'

