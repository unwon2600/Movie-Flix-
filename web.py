from flask import Flask
import threading, asyncio, time
from main import run_bot
from pyrogram import Client

app = Flask(__name__)

bot_status = {
    "connected": False,
    "username": None,
    "start_time": None,
    "last_ping": None
}

def start_bot():
    global bot_status
    try:
        bot = run_bot()  # Returns Client
        if isinstance(bot, Client):
            bot_status["connected"] = True
            bot_status["username"] = bot.me.username if bot.me else "Unknown"
            bot_status["start_time"] = time.strftime("%Y-%m-%d %H:%M:%S")

            async def ping_loop():
                while True:
                    bot_status["last_ping"] = time.strftime("%Y-%m-%d %H:%M:%S")
                    await asyncio.sleep(30)

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(ping_loop())
    except Exception as e:
        bot_status["connected"] = False
        print(f"❌ Bot failed to start: {e}")

@app.route("/")
def home():
    if bot_status["connected"]:
        html = f"""
        <center>
        <h1>🎬 Movie Flix Telegram Bot ✅</h1>
        <p><b>🤖 Username:</b> @{bot_status['username']}</p>
        <p><b>🕓 Started at:</b> {bot_status['start_time']}</p>
        <p><b>💓 Last Ping:</b> {bot_status['last_ping']}</p>
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

if __name__ == "__main__":
    threading.Thread(target=start_bot).start()
    app.run(host="0.0.0.0", port=10000)
    
