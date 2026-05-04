import sqlite3

conn = sqlite3.connect("shop.db")
cursor = conn.cursor()

# товары
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    price INTEGER,
    photo TEXT
)
""")

# заказы
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    order_text TEXT
)
""")

conn.commit()