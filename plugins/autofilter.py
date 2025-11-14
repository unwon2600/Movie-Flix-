import asyncio
import html
from urllib.parse import quote_plus
import requests

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from rapidfuzz import process
from bson import ObjectId

from main import app
from info import OMDB_API_KEY, SOURCE_CHAT_IDS, ADMINS, LOG_CHANNEL
from database.db import add_file, search_files, get_all_files_for_title, get_settings, set_setting, files_col

# ---------- Helpers ----------
def shorten_url(url: str) -> str:
    try:
        r = requests.get("https://tinyurl.com/api-create.php", params={"url": url}, timeout=6)
        if r.status_code == 200:
            return r.text
    except Exception:
        pass
    return url

def _clean_title(raw: str) -> str:
    # crude cleaning; can be improved with regex
    if not raw:
        return "Unknown"
    cleaned = raw.split('[')[0].split('(')[0].split('.')[0].strip()
    return cleaned or raw

# ---------- Auto-index incoming files from SOURCE_CHAT_IDS ----------
if SOURCE_CHAT_IDS:
    @app.on_message(filters.chat(SOURCE_CHAT_IDS) & (filters.document | filters.video | filters.audio | filters.photo))
    async def index_incoming_file(client, message):
        file_id = None
        raw_title = None
        if message.document:
            file_id = message.document.file_id
            raw_title = message.document.file_name or message.caption or ""
        elif message.video:
            file_id = message.video.file_id
            raw_title = getattr(message.video, "file_name", None) or message.caption or "video"
        elif message.audio:
            file_id = message.audio.file_id
            raw_title = getattr(message.audio, "file_name", None) or message.caption or "audio"
        elif message.photo:
            # photo is list; take the highest resolution file_id
            photo = message.photo
            file_id = photo.file_id if hasattr(photo, "file_id") else None
            raw_title = message.caption or "photo"

        if not file_id:
            return

        cleaned = _clean_title(raw_title)

        # fetch OMDb info (non-blocking by running in executor)
        imdb_id = None
        poster = None
        year = None
        if OMDB_API_KEY:
            def _omdb_lookup_title(t):
                try:
                    r = requests.get("http://www.omdbapi.com/", params={"t": t, "apikey": OMDB_API_KEY}, timeout=6)
                    if r.ok:
                        jr = r.json()
                        if jr.get("Response") == "True":
                            return jr
                except Exception:
                    pass
                return None
            loop = asyncio.get_event_loop()
            jr = await loop.run_in_executor(None, _omdb_lookup_title, cleaned)
            if jr:
                poster = jr.get("Poster")
                imdb_id = jr.get("imdbID")
                year = jr.get("Year")

        item = {
            "title": cleaned,
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
                if LOG_CHANNEL:
                    await client.send_message(LOG_CHANNEL, f"Indexed: {cleaned} from {message.chat.title or message.chat.id}")
            except Exception:
                pass

# ---------- Direct search (private) ----------
@app.on_message(filters.private & filters.text & ~filters.command())
async def direct_search(client, message):
    query = message.text.strip()
    if not query:
        return

    # force-subscribe check (placeholder: implement real AUTH channel check if needed)
    settings = await get_settings()
    if settings.get("force_subscribe", False):
        # if you have AUTH channel, check membership here
        pass

    # 1) search DB
    results = await search_files(query, limit=100)
    if results:
        first = results[0]
        imdb_id = first.get("imdb_id")
        omdb = None

        if imdb_id and OMDB_API_KEY:
            def _omdb_get(i):
                try:
                    r = requests.get("http://www.omdbapi.com/", params={"i": i, "apikey": OMDB_API_KEY}, timeout=6)
                    if r.ok:
                        return r.json()
                except Exception:
                    pass
                return None
            loop = asyncio.get_event_loop()
            omdb = await loop.run_in_executor(None, _omdb_get, imdb_id)

        if omdb and omdb.get("Response") == "True":
            title = omdb.get("Title")
            year = omdb.get("Year")
            rating = omdb.get("imdbRating", "N/A")
            plot = omdb.get("Plot","")
            poster = omdb.get("Poster")
            caption = f"🎬 <b>{html.escape(title)} ({year})</b>\n⭐ IMDb: {rating}\n\n{html.escape(plot)}\n\nAvailable Files:"
        else:
            caption = f"🔎 Results for <b>{html.escape(query)}</b>\n\nAvailable Files:"

        # group results by title, show a header then file buttons
        title_map = {}
        for doc in results[:60]:
            t = doc.get("title") or query
            title_map.setdefault(t, []).append(doc)

        buttons = []
        for t, docs in list(title_map.items())[:8]:
            # header row
            buttons.append([InlineKeyboardButton(f"🔹 {t}", callback_data=f"title|{t}")])
            row = []
            for d in docs[:6]:
                lang = d.get("language",'Unknown')
                qual = d.get("quality",'Unknown')
                label = f"{lang} {qual}"
                cb = f"getfile|{str(d.get('_id'))}"
                row.append(InlineKeyboardButton(label, callback_data=cb))
                if len(row) >= 3:
                    buttons.append(row)
                    row = []
            if row:
                buttons.append(row)

        # control row
        buttons.append([InlineKeyboardButton("Send All 🎞️", callback_data=f"sendall|{query}"),
                        InlineKeyboardButton("More Info (IMDb)", callback_data=f"imdb|{imdb_id or ''}")])
        buttons.append([InlineKeyboardButton("Year Filter", callback_data=f"year|{query}")])

        # send poster when available
        try:
            if poster:
                await client.send_photo(message.chat.id, poster, caption=caption, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="html")
            else:
                await client.send_message(message.chat.id, caption, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="html")
        except Exception:
            await client.send_message(message.chat.id, caption, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="html")
        return

    # 2) fallback to OMDb search with suggestion
    if OMDB_API_KEY:
        def _omdb_search(q):
            try:
                r = requests.get("http://www.omdbapi.com/", params={"s": q, "apikey": OMDB_API_KEY}, timeout=6)
                if r.ok:
                    return r.json()
            except Exception:
                pass
            return {}
        loop = asyncio.get_event_loop()
        jr = await loop.run_in_executor(None, _omdb_search, query)
    else:
        jr = {}

    if not jr or jr.get("Response") != "True":
        # try fuzzy suggestion using DB titles
        titles = await files_col.distinct("title")
        if titles:
            best = process.extractOne(query, titles)
            if best and best[1] >= 70:
                suggestion = best[0]
                return await client.send_message(message.chat.id, f"Did you mean: <b>{html.escape(suggestion)}</b>? Try sending that title.", parse_mode="html")
        return await client.send_message(message.chat.id, "No results found in DB or OMDb.")

    # show top OMDb match (no files)
    search_list = jr.get("Search", [])
    top = search_list[0] if search_list else None
    if not top:
        return await client.send_message(message.chat.id, "No results found.")
    imdb_id = top.get("imdbID")
    try:
        r2 = requests.get("http://www.omdbapi.com/", params={"i": imdb_id, "apikey": OMDB_API_KEY}, timeout=6)
        detail = r2.json() if r2.ok else {}
    except Exception:
        detail = {}
    if detail.get("Response") == "True":
        caption = f"🎬 <b>{html.escape(detail.get('Title',''))} ({detail.get('Year','')})</b>\n⭐ IMDb: {detail.get('imdbRating','N/A')}\n\n{html.escape(detail.get('Plot',''))}\n\nNo files found in DB. If you have these files, add them to the source group to index."
        kb = [[InlineKeyboardButton("Search IMDb ▶️", callback_data=f"imdb|{imdb_id}")]]
        if detail.get("Poster"):
            await client.send_photo(message.chat.id, detail.get("Poster"), caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="html")
        else:
            await client.send_message(message.chat.id, caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="html")
    else:
        await client.send_message(message.chat.id, "No detailed info found on OMDb.")

# ---------- Callback query handling ----------
@app.on_callback_query(filters.regex("^(getfile|sendall|imdb|title|year)\\|"))
async def cb_handler(client, callback_query):
    data = callback_query.data or ""
    user = callback_query.from_user
    parts = data.split("|", 1)
    cmd = parts[0]
    arg = parts[1] if len(parts) > 1 else ""
    is_admin = user.id in ADMINS

    if cmd == "getfile":
        _id = arg
        try:
            doc = await files_col.find_one({"_id": ObjectId(_id)})
        except Exception:
            doc = None
        if not doc:
            return await callback_query.answer("File not found.", show_alert=True)
        try:
            await client.copy_message(chat_id=callback_query.message.chat.id,
                                      from_chat_id=doc["chat_id"],
                                      message_id=doc["message_id"])
            await callback_query.answer("Sending file...")
        except Exception:
            await callback_query.answer("Failed to send file (bot may not have access).", show_alert=True)

    elif cmd == "sendall":
        query = arg
        await callback_query.answer("Sending all matches... This may take time.")
        matches = await search_files(query, limit=500)
        sent = 0
        for doc in matches:
            try:
                await client.copy_message(chat_id=callback_query.message.chat.id,
                                          from_chat_id=doc["chat_id"],
                                          message_id=doc["message_id"])
                sent += 1
                await asyncio.sleep(0.25)
            except Exception:
                continue
        await callback_query.message.reply_text(f"Sent {sent} files for '{query}'")

    elif cmd == "imdb":
        imdb_id = arg
        if not imdb_id:
            return await callback_query.answer("No IMDb ID available.", show_alert=True)
        try:
            r = requests.get("http://www.omdbapi.com/", params={"i": imdb_id, "apikey": OMDB_API_KEY}, timeout=6)
            movie = r.json() if r.ok else {}
        except Exception:
            movie = {}
        if not movie or movie.get("Response") != "True":
            return await callback_query.answer("Failed to fetch IMDb data.", show_alert=True)
        text = f"🎬 {movie.get('Title')} ({movie.get('Year','')})\n⭐ IMDb: {movie.get('imdbRating','N/A')}\n\n{movie.get('Plot','')}"
        await callback_query.message.reply_text(text)

    elif cmd == "title":
        exact_title = arg
        matches = await get_all_files_for_title(exact_title)
        if not matches:
            return await callback_query.answer("No files for that title.", show_alert=True)
        btns = []
        for d in matches[:25]:
            label = f"{d.get('language','Unknown')} {d.get('quality','Unknown')}"
            btns.append([InlineKeyboardButton(label, callback_data=f"getfile|{str(d.get('_id'))}")])
        await callback_query.message.reply_text(f"Files for <b>{html.escape(exact_title)}</b>:", reply_markup=InlineKeyboardMarkup(btns), parse_mode="html")

    elif cmd == "year":
        q = arg
        docs = await search_files(q, limit=200)
        years = {}
        for d in docs:
            y = d.get("year") or "Unknown"
            years.setdefault(y, 0)
            years[y] += 1
        btns = []
        for y, cnt in sorted(years.items(), reverse=True):
            btns.append([InlineKeyboardButton(f"{y} ({cnt})", callback_data=f"yearfilter|{q}|{y}")])
        if not btns:
            return await callback_query.answer("No year info available.", show_alert=True)
        await callback_query.message.reply_text("Choose year:", reply_markup=InlineKeyboardMarkup(btns))

# ---------- yearfilter callback ----------
@app.on_callback_query(filters.regex("^yearfilter\\|"))
async def yearfilter_cb(client, callback_query):
    parts = callback_query.data.split("|", 2)
    if len(parts) < 3:
        return await callback_query.answer()
    _, query, year = parts
    matches = await files_col.find({"title": {"$regex": query, "$options": "i"}, "year": year}).to_list(200)
    if not matches:
        return await callback_query.answer("No matches for that year.", show_alert=True)
    sent = 0
    for d in matches:
        try:
            await client.copy_message(chat_id=callback_query.message.chat.id,
                                      from_chat_id=d["chat_id"],
                                      message_id=d["message_id"])
            sent += 1
            await asyncio.sleep(0.2)
        except Exception:
            continue
    await callback_query.message.reply_text(f"Sent {sent} files for {query} ({year})")

# ---------- Admin commands ----------
@app.on_message(filters.private & filters.command("shortener") & filters.user(ADMINS))
async def cmd_shortener(client, message):
    # /shortener on|off
    if len(message.command) < 2:
        return await message.reply_text("Usage: /shortener on|off")
    val = message.command[1].lower() == "on"
    await set_setting("shortener", val)
    await message.reply_text(f"Shortener set to {val}")

@app.on_message(filters.private & filters.command("fsub") & filters.user(ADMINS))
async def cmd_fsub(client, message):
    # /fsub on|off
    if len(message.command) < 2:
        return await message.reply_text("Usage: /fsub on|off")
    val = message.command[1].lower() == "on"
    await set_setting("force_subscribe", val)
    await message.reply_text(f"Force-subscribe set to {val}")
