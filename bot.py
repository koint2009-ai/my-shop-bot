import asyncio
import sqlite3

from aiogram import Bot, Dispatcher, F
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

# 🧠 состояние
temp_product = {}

# 🚀 START
@dp.message(F.text == "/start")
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


# 🛒 ЗАКАЗ С САЙТА
@dp.message(F.web_app_data)
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
@dp.message(F.text == "/admin")
async def admin(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    await message.answer(
        "👨‍💼 Админка\n\n"
        "/add - добавить товар\n"
        "/products - список\n"
        "/delete ID - удалить товар"
    )


# ➕ СТАРТ ДОБАВЛЕНИЯ
@dp.message(F.text == "/add")
async def add_product(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    temp_product[message.from_user.id] = {"step": "text"}
    await message.answer("Введи: Название,Цена\nПример:\nHoodie,50")


# 📝 ТЕКСТ (название + цена)
@dp.message(F.text)
async def handle_text(message: Message):
    user_id = message.from_user.id

    if user_id != ADMIN_ID:
        return

    if user_id not in temp_product:
        return

    state = temp_product[user_id]

    if state["step"] != "text":
        return

    if "," not in message.text:
        await message.answer("❌ Формат: Название,Цена")
        return

    try:
        name, price = message.text.split(",")

        temp_product[user_id] = {
            "step": "photo",
            "name": name.strip(),
            "price": int(price.strip())
        }

        await message.answer("Теперь отправь фото 📸")
    except:
        await message.answer("❌ Ошибка формата")


# 📸 ФОТО (срабатывает ВСЕГДА)
@dp.message(F.photo)
async def handle_photo(message: Message):
    user_id = message.from_user.id

    if user_id != ADMIN_ID:
        return

    if user_id not in temp_product:
        return

    state = temp_product[user_id]

    if state["step"] != "photo":
        return

    file_id = message.photo[-1].file_id

    cursor.execute(
        "INSERT INTO products (name, price, photo) VALUES (?, ?, ?)",
        (state["name"], state["price"], file_id)
    )
    conn.commit()

    del temp_product[user_id]

    await message.answer("✅ Товар добавлен!")


# 📋 СПИСОК
@dp.message(F.text == "/products")
async def list_products(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    if not products:
        await message.answer("❌ Товаров нет")
        return

    for p in products:
        await message.answer_photo(
            p[3],
            caption=f"ID: {p[0]}\n{p[1]} - {p[2]}€"
        )


# ❌ УДАЛЕНИЕ
@dp.message(F.text.startswith("/delete"))
async def delete_product(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        product_id = int(message.text.split()[1])

        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()

        await message.answer("🗑 Товар удалён")
    except:
        await message.answer("❌ Пример: /delete 1")


# ▶️ ЗАПУСК
async def main():
    print("🔥 Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
