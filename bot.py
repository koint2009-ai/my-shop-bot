import asyncio
import sqlite3
import os

from aiogram import Bot, Dispatcher
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo
)

# 🔑 Railway Variables
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# 🤖 BOT
bot = Bot(token=TOKEN)
dp = Dispatcher()

# 📦 DATABASE
conn = sqlite3.connect("shop.db", check_same_thread=False)
cursor = conn.cursor()

# 🧱 TABLES
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

# 🧠 STATES
states = {}

# 🚀 START
@dp.message(lambda m: m.text == "/start")
async def start(message: Message):

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="🛍 Открыть магазин",
                    web_app=WebAppInfo(
                        url="https://gorgeous-zabaione-63939c.netlify.app"
                    )
                )
            ]
        ],
        resize_keyboard=True
    )

    await message.answer(
        "👋 Добро пожаловать!",
        reply_markup=kb
    )

# 🛒 ORDER
@dp.message(lambda m: m.web_app_data)
async def get_order(message: Message):

    order = message.web_app_data.data

    cursor.execute(
        "INSERT INTO orders (user_id, username, order_text) VALUES (?, ?, ?)",
        (
            message.from_user.id,
            message.from_user.username,
            order
        )
    )

    conn.commit()

    await message.answer("✅ Заказ отправлен!")

    username = message.from_user.username

    if username:
        username = f"@{username}"
    else:
        username = "без username"

    await bot.send_message(
        ADMIN_ID,
        f"🛒 Новый заказ\n\n{order}\n\n👤 {username}"
    )

# 👨‍💼 ADMIN
@dp.message(lambda m: m.text == "/admin" and m.from_user.id == ADMIN_ID)
async def admin(message: Message):

    await message.answer(
        "👨‍💼 Админка\n\n"
        "/add - добавить товар\n"
        "/products - список товаров\n"
        "/delete ID - удалить товар"
    )

# ➕ ADD PRODUCT
@dp.message(lambda m: m.text == "/add" and m.from_user.id == ADMIN_ID)
async def add_product(message: Message):

    states[message.from_user.id] = {
        "step": "text"
    }

    await message.answer(
        "Введи:\n\nНазвание,Цена\n\nПример:\nHoodie,50"
    )

# 🧾 TEXT STEP
@dp.message(lambda m: m.text and "," in m.text and m.from_user.id == ADMIN_ID)
async def handle_text(message: Message):

    user_id = message.from_user.id

    if user_id not in states:
        return

    try:

        name, price = message.text.split(",")

        states[user_id] = {
            "step": "photo",
            "name": name.strip(),
            "price": int(price.strip())
        }

        await message.answer("📸 Теперь отправь фото товара")

    except:
        await message.answer("❌ Ошибка формата")

# 📸 PHOTO STEP
@dp.message(lambda m: m.photo and m.from_user.id == ADMIN_ID)
async def handle_photo(message: Message):

    user_id = message.from_user.id

    if user_id not in states:
        return

    state = states[user_id]

    if state["step"] != "photo":
        return

    try:

        file_id = message.photo[-1].file_id

        file = await bot.get_file(file_id)

        photo_url = f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}"

        cursor.execute(
            "INSERT INTO products (name, price, photo) VALUES (?, ?, ?)",
            (
                state["name"],
                state["price"],
                photo_url
            )
        )

        conn.commit()

        del states[user_id]

        await message.answer("✅ Товар добавлен!")

    except Exception as e:

        await message.answer(f"❌ Ошибка:\n{e}")
# 📋 PRODUCTS
@dp.message(lambda m: m.text == "/products" and m.from_user.id == ADMIN_ID)
async def list_products(message: Message):

    try:

        cursor.execute("SELECT * FROM products")

        products = cursor.fetchall()

        if not products:
            await message.answer("❌ Товаров нет")
            return

        for p in products:

            try:

                await message.answer_photo(
                    photo=p[3],
                    caption=f"ID: {p[0]}\n{p[1]} - {p[2]}€"
                )

            except Exception:

                await message.answer(
                    f"ID: {p[0]}\n{p[1]} - {p[2]}€\n\n❌ Фото не загрузилось"
                )

    except Exception as e:

        await message.answer(f"❌ Ошибка:\n{e}")

# ❌ DELETE
@dp.message(lambda m: m.text.startswith("/delete") and m.from_user.id == ADMIN_ID)
async def delete_product(message: Message):

    try:

        product_id = int(message.text.split()[1])

        cursor.execute(
            "DELETE FROM products WHERE id = ?",
            (product_id,)
        )

        conn.commit()

        await message.answer("🗑 Товар удалён")

    except:
        await message.answer("❌ Используй:\n/delete 1")

# ▶️ START BOT
async def main():

    print("🔥 BOT STARTED")

    await dp.start_polling(bot)

# 🚀 RUN
if __name__ == "__main__":
    asyncio.run(main())
