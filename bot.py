import asyncio
import sqlite3

from aiogram import Bot, Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

# 🔑 ВСТАВЬ СВОЙ ТОКЕН
TOKEN = "8701068910:AAEZ6dyd8bnIh8Wz0Ce_Lhxmsu66sGpyArM"

# 👤 ВСТАВЬ СВОЙ ID
ADMIN_ID = 1117190340

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 📦 БАЗА
conn = sqlite3.connect("shop.db")
cursor = conn.cursor()

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

# 🧠 ВРЕМЕННОЕ ХРАНЕНИЕ
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
    order = message.web_app_data.data

    cursor.execute(
        "INSERT INTO orders (user_id, username, order_text) VALUES (?, ?, ?)",
        (message.from_user.id, message.from_user.username, order)
    )
    conn.commit()

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


# ➕ ШАГ 1: название и цена
@dp.message(lambda m: m.text == "/add" and m.from_user.id == ADMIN_ID)
async def add_product(message: Message):
    temp_product[message.from_user.id] = {}
    await message.answer("Введи: Название,Цена\nПример:\nHoodie,50")


# ➕ ШАГ 2: сохраняем текст
@dp.message(lambda m: m.from_user.id == ADMIN_ID and "," in m.text)
async def save_text(message: Message):
    if message.from_user.id not in temp_product:
        return

    name, price = message.text.split(",")
    temp_product[message.from_user.id]["name"] = name.strip()
    temp_product[message.from_user.id]["price"] = int(price)

    await message.answer("Теперь отправь фото товара 📸")


# ➕ ШАГ 3: сохраняем фото
@dp.message(lambda m: m.photo and m.from_user.id == ADMIN_ID)
async def save_photo(message: Message):
    if message.from_user.id not in temp_product:
        return

    file_id = message.photo[-1].file_id

    data = temp_product[message.from_user.id]

    cursor.execute(
        "INSERT INTO products (name, price, photo) VALUES (?, ?, ?)",
        (data["name"], data["price"], file_id)
    )
    conn.commit()

    del temp_product[message.from_user.id]

    await message.answer("✅ Товар с фото добавлен")


# 📋 СПИСОК
@dp.message(lambda m: m.text == "/products" and m.from_user.id == ADMIN_ID)
async def list_products(message: Message):
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    if not products:
        await message.answer("Нет товаров")
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

        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()

        await message.answer("🗑 Товар удалён")

    except:
        await message.answer("❌ Ошибка. Пример: /delete 1")


# ▶️ ЗАПУСК
async def main():
    print("🔥 Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())