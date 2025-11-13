# web.py
from flask import Flask, jsonify, render_template_string
import threading, time
from main import run_bot
from pyrogram import Client

app = Flask(__name__)

bot_status = {
    "connected": False,
    "username": None,
    "start_time": None
}

# Start the bot in this thread (called from wsgi on worker start)
def start_bot_thread():
    global bot_status
    try:
        bot = run_bot()  # run_bot returns a started pyrogram Client
        if isinstance(bot, Client):
            bot_status["connected"] = True
            # bot.me may be None for a short time; guard it
            bot_status["username"] = getattr(bot.me, "username", None) or "unknown"
            bot_status["start_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        bot_status["connected"] = False
        print("Bot failed to start:", e)

# Flask routes
@app.route("/")
def home():
    if bot_status["connected"]:
        html = f"""
        <center style="font-family: Arial, Helvetica, sans-serif; margin-top:50px;">
            <h1>🎬 Movie Flix Bot ✅</h1>
            <p><b>🤖 Username:</b> @{bot_status['username']}</p>
            <p><b>🕓 Started at:</b> {bot_status['start_time']}</p>
            <p><b>Status:</b> <span style='color:green;'>Connected</span></p>
        </center>
        """
    else:
        html = """
        <center style="font-family: Arial, Helvetica, sans-serif; margin-top:50px;">
            <h1>❌ Movie Flix Bot Not Connected</h1>
            <p>Check Render logs or wait a few seconds.</p>
        </center>
        """
    return render_template_string(html)

@app.route("/status")
def status():
    return jsonify(bot_status)

# Expose start function for wsgi loader to call
def launch_background_bot():
    t = threading.Thread(target=start_bot_thread, daemon=True)
    t.start()
    
