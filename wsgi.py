# wsgi.py
from web import app, launch_background_bot

# Launch the bot when the WSGI module is imported by Gunicorn
launch_background_bot()

# `app` is the Flask application object for Gunicorn
if __name__ == "__main__":
    # Useful for local testing (not used by Gunicorn on Render)
    app.run(host="0.0.0.0", port=10000)
from web import app

# WSGI entry point for Gunicorn
if __name__ == "__main__":
    app.run()
    
