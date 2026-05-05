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


# ➕ ШАГ 1
@dp.message(lambda m: m.text == "/add" and m.from_user.id == ADMIN_ID)
async def add_product(message: Message):
    temp_product[message.from_user.id] = {"step": "text"}
    await message.answer("Введи: Название,Цена\nПример:\nHoodie,50")


# 🔥 ОБРАБОТКА ДОБАВЛЕНИЯ
@dp.message()
async def handle_add(message: Message):
    user_id = message.from_user.id

    if user_id != ADMIN_ID:
        return

    if user_id not in temp_product:
        return

    state = temp_product[user_id]

    # 🧠 ШАГ 1 — текст
    if state.get("step") == "text":
        if not message.text:
            return

        if "," not in message.text:
            await message.answer("❌ Формат: Название,Цена")
            return

        try:
            name, price = message.text.split(",")

            temp_product[user_id]["step"] = "photo"
            temp_product[user_id]["name"] = name.strip()
            temp_product[user_id]["price"] = int(price.strip())

            await message.answer("📸 Теперь отправь фото товара")
        except:
            await message.answer("❌ Ошибка формата")
        return

    # 📸 ШАГ 2 — фото
    if state.get("step") == "photo":
        if not message.photo:
            await message.answer("❌ Отправь именно фото")
            return

        # 🔒 защита
        if "name" not in state or "price" not in state:
            await message.answer("❌ Ошибка состояния. Напиши /add заново")
            temp_product.pop(user_id, None)
            return

        file_id = message.photo[-1].file_id

        cursor.execute(
            "INSERT INTO products (name, price, photo) VALUES (?, ?, ?)",
            (state["name"], state["price"], file_id)
        )
        conn.commit()

        temp_product.pop(user_id, None)

        await message.answer("✅ Товар добавлен!")


# 📋 СПИСОК
@dp.message(lambda m: m.text == "/products" and m.from_user.id == ADMIN_ID)
async def list_products(message: Message):
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
@dp.message(lambda m: m.text.startswith("/delete") and m.from_user.id == ADMIN_ID)
async def delete_product(message: Message):
    try:
        product_id = int(message.text.split()[1])

        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()

        await message.answer("🗑 Товар удалён")
    except:
        await message.answer("❌ Пример: /delete 1")


# ▶️ ЗАПУСК
async def main():
    print("🔥 BOT STARTED")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
