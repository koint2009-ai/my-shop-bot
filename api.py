from flask import Flask, jsonify
from flask_cors import CORS
import sqlite3
import threading
import asyncio
import os

from bot import dp, bot

app = Flask(__name__)

# ✅ ENABLE CORS
CORS(app)

# 📦 DATABASE
def get_db():

    conn = sqlite3.connect("shop.db")
    conn.row_factory = sqlite3.Row

    return conn

# 🌐 PRODUCTS API
@app.route("/products")
def products():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products")

    data = cursor.fetchall()

    result = []

    for row in data:

        result.append({
            "id": row["id"],
            "name": row["name"],
            "price": row["price"],
            "photo": row["photo"]
        })

    conn.close()

    return jsonify(result)

# 🏠 HOME
@app.route("/")
def home():

    return "API WORKING"

# 🤖 RUN BOT
def run_bot():

    loop = asyncio.new_event_loop()

    asyncio.set_event_loop(loop)

    async def start():

        try:
            await bot.delete_webhook(drop_pending_updates=True)
        except:
            pass

        await dp.start_polling(bot, handle_signals=False)

    loop.run_until_complete(start())

# 🚀 START
if __name__ == "__main__":

    threading.Thread(
        target=run_bot,
        daemon=True
    ).start()

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
