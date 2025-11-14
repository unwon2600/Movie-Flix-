import os
import threading
from flask import Flask
from main import run_bot

app = Flask(__name__)

# Bot status info
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
        bot = run_bot()  # Make sure run_bot() returns the Client instance
        from pyrogram import Client
        if isinstance(bot, Client):
            bot_status["connected"] = True
            bot_status["username"] = bot.me.username if bot.me else "Unknown"
            import time
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
    # Start bot in a separate thread
    threading.Thread(target=start_bot).start()

    # Render assigns a dynamic port
    PORT = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=PORT)
    
