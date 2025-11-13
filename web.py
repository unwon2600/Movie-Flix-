from flask import Flask
import threading, asyncio, time
from main import run_bot
from pyrogram import Client

app = Flask(__name__)

bot_status = {
    "connected": False,
    "username": None,
    "start_time": None
}

# --- BOT THREAD FUNCTION ---
def start_bot():
    global bot_status
    try:
        print("🎬 Starting Movie Flix Bot...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        bot = run_bot()  # should return a Client
        if isinstance(bot, Client):
            bot_status["connected"] = True
            bot_status["username"] = bot.me.username if bot.me else "Unknown"
            bot_status["start_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            bot_status["connected"] = False
    except Exception as e:
        bot_status["connected"] = False
        print(f"❌ Bot failed to start: {e}")

# --- ROUTES ---
@app.route("/")
def home():
    if bot_status["connected"]:
        html = f"""
        <center>
        <h1>🎬 Movie Flix Telegram Bot ✅</h1>
        <p><b>🤖 Username:</b> @{bot_status['username']}</p>
        <p><b>🕓 Started at:</b> {bot_status['start_time']}</p>
        <p><b>Status:</b> <span style='color:green;'>Connected</span></p>
        </center>
        """
    else:
        html = """
        <center>
        <h1>❌ Movie Flix Bot Not Connected</h1>
        <p>Please wait a few seconds or check Render logs.</p>
        </center>
        """
    return html

# --- STARTUP ---
if __name__ == "__main__":
    threading.Thread(target=start_bot).start()
    app.run(host="0.0.0.0", port=10000)
    
