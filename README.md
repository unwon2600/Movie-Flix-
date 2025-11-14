# Movie Flix Filter Bot (Render-ready)

1. Copy `.env.example` to `.env` and fill values (API keys, MONGO_URI, BOT_TOKEN, etc).
2. Ensure `.env` is not committed (add to `.gitignore`).
3. Commit & push to GitHub.
4. On Render: Create a new service (Worker), connect repo.
   - Build command: `pip install -r requirements.txt`
   - Start command: `python3 main.py`
   - Add Environment Variables as in `.env`
5. Deploy. Watch logs for startup messages.
