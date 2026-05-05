import asyncio
import sqlite3

from aiogram import Bot, Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

TOKEN = "8701068910:AAGZtEQvzrRNVCQJzrwevIYIaNLLmvQC8Ko"
ADMIN_ID = 1117190340

bot = Bot(token=TOKEN)
dp = Dispatcher()


# 📦 БАЗА
def get_db():
    conn = sqlite3.connect("shop.db", check_same_thread=False)
    return conn, conn.cursor()


# 🔧 СОЗДАНИЕ ТАБЛИЦ
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


# 🧠 СОСТОЯНИЕ
temp_product = {}


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


# 🛒 ЗАКАЗ
@dp.message(lambda m: m.web_app_data)
async def get_order(message: Message):
    conn, cursor = get_db()

    order = message.web_app_data.data

    cursor.execute(
        "INSERT INTO orders (user_id, username, order_text) VALUES (?, ?, ?)",
        (message.from_user.id, message.from_user.username, order)
    )

    conn.commit()
    conn.close()

    await message.answer("✅ Заказ отправлен!")

    await bot.send_message(
        ADMIN_ID,
        f"🛒 Новый заказ:\n\n{order}\n👤 @{message.from_user.username}"
    )


# 👨‍💼 АДМИНКА
@dp.message(lambda m: m.text == "/admin" and m.from_user.id == ADMIN_ID)
async def admin(message: Message):
    await message.answer(
        "👨‍💼 Админка\n\n"
        "/add - добавить товар\n"
        "/products - список\n"
        "/delete ID - удалить товар"
    )


# ➕ СТАРТ
@dp.message(lambda m: m.text == "/add" and m.from_user.id == ADMIN_ID)
async def add_product(message: Message):
    temp_product[message.from_user.id] = {"step": "text"}
    await message.answer("Введи: Название,Цена\nПример:\nHoodie,50")


# 📸 ФОТО
@dp.message(lambda m: m.photo and m.from_user.id == ADMIN_ID)
async def handle_photo(message: Message):
    try:
        user_id = message.from_user.id

        if user_id not in temp_product:
            return

        state = temp_product[user_id]

        if state.get("step") != "photo":
            return

        file_id = message.photo[-1].file_id

        conn, cursor = get_db()

        cursor.execute(
            "INSERT INTO products (name, price, photo) VALUES (?, ?, ?)",
            (state["name"], state["price"], file_id)
        )

        conn.commit()
        conn.close()

        temp_product.pop(user_id, None)

        await message.answer("✅ Товар добавлен!")

    except Exception as e:
        print("ERROR:", e)
        await message.answer("❌ Ошибка при сохранении")

# 🧾 ТЕКСТ
@dp.message(lambda m: m.from_user.id == ADMIN_ID and m.text and "," in m.text)
async def handle_text(message: Message):
    user_id = message.from_user.id

    if user_id not in temp_product:
        return

    try:
        name, price = message.text.split(",")

        temp_product[user_id] = {
            "step": "photo",
            "name": name.strip(),
            "price": int(price.strip())
        }

        await message.answer("📸 Теперь отправь фото товара")
    except:
        await message.answer("❌ Ошибка формата")


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
    init_db()
    print("🔥 BOT STARTED")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
