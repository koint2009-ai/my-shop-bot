from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect("shop.db")
    conn.row_factory = sqlite3.Row
    return conn

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

if __name__ == "__main__":
    app.run(port=5000)