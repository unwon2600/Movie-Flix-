from flask import Flask
import threading
import time
import os
from main import run_bot
from pyrogram.errors import FloodWait

app = Flask(__name__)

@app.route('/')
def home():
    return "🎬 Movie Flix Bot is Live!"

@app.route('/status')
def status():
    return {"status": "ok", "bot": "running"}

def start_bot():
    while True:
        try:
            print("🎬 Starting Movie Flix Bot...")
            run_bot()
        except FloodWait as e:
            print(f"⚠️ FloodWait: sleeping for {e.value} seconds...")
            time.sleep(e.value)
        except Exception as err:
            print(f"❌ Bot crashed: {err}")
            print("🔁 Restarting in 10 seconds...")
            time.sleep(10)

if __name__ == '__main__':
    threading.Thread(target=start_bot).start()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
