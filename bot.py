import asyncio
import sqlite3
import os

from aiogram import Bot, Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

# 🔑 берём из Railway Variables
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 📦 БАЗА
def get_db():
    conn = sqlite3.connect("shop.db", check_same_thread=False)
    return conn, conn.cursor()

def init_db():
    conn, cursor = get_db()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price INTEGER,
        photo TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT,
        order_text TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# 🧠 СОСТОЯНИЕ (просто и надёжно)
user_state = {}

# 🚀 START
@dp.message(lambda m: m.text == "/start")
async def start(message: Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(
                text="🛍 Открыть магазин",
                web_app=WebAppInfo(
                    url="https://gorgeous-zabaione-63939c.netlify.app"
                )
            )]
        ],
        resize_keyboard=True
    )
    await message.answer("👋 Добро пожаловать!", reply_markup=kb)


# 👨‍💼 АДМИН
@dp.message(lambda m: m.text == "/admin" and m.from_user.id == ADMIN_ID)
async def admin(message: Message):
    await message.answer(
        "👨‍💼 Админка\n\n"
        "/add - добавить товар\n"
        "/products - список\n"
        "/delete ID - удалить"
    )


# ➕ НАЧАЛО ДОБАВЛЕНИЯ
@dp.message(lambda m: m.text == "/add" and m.from_user.id == ADMIN_ID)
async def add(message: Message):
    user_state[message.from_user.id] = {"step": "text"}
    await message.answer("Введи: Название,Цена\nПример:\nHoodie,50")


# 🧾 ШАГ 1 — ТЕКСТ
@dp.message(lambda m: m.from_user.id == ADMIN_ID and m.text and "," in m.text)
async def handle_text(message: Message):
    user_id = message.from_user.id

    if user_id not in user_state:
        return

    if user_state[user_id]["step"] != "text":
        return

    try:
        name, price = message.text.split(",")

        user_state[user_id] = {
            "step": "photo",
            "name": name.strip(),
            "price": int(price.strip())
        }

        await message.answer("📸 Теперь отправь фото товара")
    except:
        await message.answer("❌ Ошибка формата")


# 📸 ШАГ 2 — ФОТО (ЖЁСТКО ЛОВИМ ТОЛЬКО ФОТО)
@dp.message(lambda m: m.from_user.id == ADMIN_ID and m.photo)
async def handle_photo(message: Message):
    user_id = message.from_user.id

    if user_id not in user_state:
        return

    if user_state[user_id]["step"] != "photo":
        return

    file_id = message.photo[-1].file_id

    conn, cursor = get_db()

    cursor.execute(
        "INSERT INTO products (name, price, photo) VALUES (?, ?, ?)",
        (user_state[user_id]["name"], user_state[user_id]["price"], file_id)
    )

    conn.commit()
    conn.close()

    user_state.pop(user_id, None)

    await message.answer("✅ Товар добавлен!")


# 📋 СПИСОК
@dp.message(lambda m: m.text == "/products" and m.from_user.id == ADMIN_ID)
async def list_products(message: Message):
    conn, cursor = get_db()

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    conn.close()

    if not products:
        await message.answer("❌ Товаров нет")
        return

    for p in products:
        await message.answer_photo(
            p[3],
            caption=f"ID: {p[0]}\n{p[1]} - {p[2]}€"
        )


# ❌ УДАЛЕНИЕ
@dp.message(lambda m: m.text.startswith("/delete") and m.from_user.id == ADMIN_ID)
async def delete_product(message: Message):
    try:
        product_id = int(message.text.split()[1])

        conn, cursor = get_db()
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        conn.close()

        await message.answer("🗑 Товар удалён")
    except:
        await message.answer("❌ Пример: /delete 1")


# ▶️ ЗАПУСК
async def main():
    print("🔥 BOT STARTED")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
