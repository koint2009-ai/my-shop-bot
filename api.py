from flask import Flask, jsonify
import sqlite3
import threading
import asyncio

from bot import dp, bot

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect("shop.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price INTEGER,
        photo TEXT
    )
    """)

    conn.commit()
    conn.close()

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

    return jsonify(result)

@app.route("/")
def home():
    return "API WORKING"

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(dp.start_polling(bot, handle_signals=False))

# 🔥 ВАЖНО — запускается ВСЕГДА
init_db()
threading.Thread(target=run_bot, daemon=True).start()
