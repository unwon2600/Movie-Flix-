from flask import Flask
import threading
import os
from main import run_bot

app = Flask(__name__)

@app.route("/")
def home():
    return "🎬 Movie Flix Bot is Running!"

# --- Start Bot in Background ---
threading.Thread(target=run_bot).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    
