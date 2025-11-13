from flask import Flask
import os
from threading import Thread
from main import run_bot

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Movie Flix Bot is Running Successfully!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    # Run Flask in one thread
    Thread(target=run_flask).start()
    # Run Telegram bot in another
    run_bot()
  
