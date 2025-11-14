import os
from flask import Flask
from main import run_bot
import threading

app = Flask(__name__)

# Get port from Render environment variable
PORT = int(os.environ.get("PORT", 10000))

# Start bot in a separate thread
threading.Thread(target=run_bot).start()

@app.route("/")
def home():
    return "<h1>🎬 Movie Flix Bot is running!</h1>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
    
