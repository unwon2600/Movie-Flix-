from flask import Flask
import threading
from main import run_bot

app = Flask(__name__)

bot_status = {"connected": False}

# --- BOT THREAD FUNCTION ---
def start_bot():
    global bot_status
    try:
        run_bot()
        bot_status["connected"] = True
    except Exception as e:
        bot_status["connected"] = False
        print(f"Bot Error: {e}")

# --- ROUTES ---
@app.route("/")
def home():
    if bot_status["connected"]:
        return "<h2>🎬 Movie Flix Bot Connected ✅</h2>"
    else:
        return "<h2>❌ Bot Not Connected Yet</h2>"

# --- STARTUP ---
if __name__ == "__main__":
    threading.Thread(target=start_bot).start()
    app.run(host="0.0.0.0", port=10000)
    
