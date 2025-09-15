import os
import json
import math
import threading
from flask import Flask
from telegram import (
    Update, 
    ReplyKeyboardMarkup, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton
)
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler, 
    filters, 
    ContextTypes
)

# === Flask-заглушка, чтобы Render видел открытый порт ===
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Bot is running on Render!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))  # Render передает порт в переменной PORT
    app.run(host="0.0.0.0", port=port)

# === Загружаем справочник разъёмов ===
with open("connectors.json", encoding="utf-8") as f:
    CONNECTORS = json.load(f)

# === Токен и настройки ===
TOKEN = os.getenv("BOT_TOKEN")
OWNER_LINK = "https://t.me/ermakov_remont"
ADMIN_ID = 437753009   # твой ID, заявки будут приходить сюда
USER_CONTEXT = {}

# === Функции ===
def round_up_to_100(x):
    return int(math.ceil(x / 100.0)) * 100

def calculate_price(model: str, repair_type: str) -> str:
    model_lower = model.lower()
    connector = None

    for key, conn in CONNECTORS.items():
        if key.lower() in model_lower:
            connector = conn
            break

    if not connector and "iphone" in model_lower:
        connector = "Lightning"

    if not connector:
        return "❌ Не удалось определить модель или разъём."

    if repair_type == "экран":
        total = round_up_to_100(3000)  # + цена детали (можно добавить парсер)
        return f"💡 Замена дисплея для {model}: {total} ₽ (срок 1 день)"

    if repair_type == "батарея":
        if "iphone" in model_lower:
            total = round_up_to_100(2500)
        else:
            total = round_up_to_100(2000)
        return f"🔋 Замена аккумулятора для {model}: {total} ₽ (срок 1 день)"

    if repair_type == "разъем":
        if connector == "MicroUSB":
            total = round_up_to_100(1200)
        elif connector == "Type-C":
            total = round_up_to_100(2000)
        else:
            total = "По запросу"
        return f"🔌 Замена разъёма ({connector}) для {model}: {total} ₽ (срок 1 день)"

    return f"ℹ️ {model} ({connector}) — уточните, какую услугу рассчитать."

# === Обработчики ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["О нас", "Помощь", "Связаться"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Привет! 👋 Я бот сервиса РемПлюс.\nВыберите действие:", reply_markup=reply_markup)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.lower()

    if "о нас" in text:
        await update.message.reply_text("👨‍🔧 РемПлюс — профессиональный ремонт смартфонов.\nТелефон: +79120412121")
        return
    if "помощь" in text:
        await update.message.reply_text("❓ Напишите модель телефона и услугу (экран, батарея, разъём), а я рассчитаю цену.")
        return
    if "связаться" in text:
        await update.message.reply_text(f"📞 Напишите нам: {OWNER_LINK}")
        return

    # Модель
    if any(b in text for b in ["iphone", "samsung", "xiaomi", "huawei", "honor", "realme", "oppo", "infinix", "tecno"]):
        if user_id not in USER_CONTEXT:
            USER_CONTEXT[user_id] = {"model": None, "service": None}
        USER_CONTEXT[user_id]["model"] = update.message.text
        if USER_CONTEXT[user_id]["service"]:
            price = calculate_price(USER_CONTEXT[user_id]["model"], USER_CONTEXT[user_id]["service"])
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🛒 Оформить заявку", callback_data="order")]])
            await update.message.reply_text(price, reply_markup=keyboard)
        else:
            await update.message.reply_text(f"📱 Модель: {update.message.text}\nТеперь укажите услугу (экран, батарея, разъём).")
        return

    # Услуга
    service = None
    if "экран" in text or "дисплей" in text:
        service = "экран"
    elif "батаре" in text or "аккум" in text:
        service = "батарея"
    elif "разъем" in text or "заряд" in text or "порт" in text:
        service = "разъем"

    if service:
        if user_id not in USER_CONTEXT:
            USER_CONTEXT[user_id] = {"model": None, "service": None}
        USER_CONTEXT[user_id]["service"] = service
        if USER_CONTEXT[user_id]["model"]:
            price = calculate_price(USER_CONTEXT[user_id]["model"], USER_CONTEXT[user_id]["service"])
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🛒 Оформить заявку", callback_data="order")]])
            await update.message.reply_text(price, reply_markup=keyboard)
        else:
            await update.message.reply_text(f"✏️ Укажите модель телефона для {service}.")
        return

    await update.message.reply_text("⚡ Напишите модель телефона и услугу (например: «замена экрана iPhone 12»).")

# === Inline-кнопки ===
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "order":
        USER_CONTEXT[query.from_user.id]["stage"] = "name"
        await query.message.reply_text("✍️ Давайте оформим заявку!\nКак вас зовут?")

async def order_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    if user_id not in USER_CONTEXT or "stage" not in USER_CONTEXT[user_id]:
        return

    stage = USER_CONTEXT[user_id]["stage"]

    if stage == "name":
        USER_CONTEXT[user_id]["name"] = text
        USER_CONTEXT[user_id]["stage"] = "phone"
        await update.message.reply_text("📞 Укажите ваш номер телефона:")
    elif stage == "phone":
        USER_CONTEXT[user_id]["phone"] = text
        name = USER_CONTEXT[user_id].get("name")
        phone = USER_CONTEXT[user_id].get("phone")
        model = USER_CONTEXT[user_id].get("model")
        service = USER_CONTEXT[user_id].get("service")

        card = (
            f"🆕 <b>Новая заявка</b>\n\n"
            f"👤 Имя: <b>{name}</b>\n"
            f"📞 Телефон: <b>{phone}</b>\n"
            f"📱 Модель: <b>{model}</b>\n"
            f"🛠 Услуга: <b>{service}</b>"
        )

        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("📩 Написать клиенту", url=f"tel:{phone}")]]
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID, 
            text=card, 
            parse_mode="HTML", 
            reply_markup=keyboard
        )

        await update.message.reply_text("✅ Спасибо! Ваша заявка принята, мы скоро свяжемся с вами.")
        USER_CONTEXT[user_id] = {}

# === Запуск ===
def main():
    app_tg = Application.builder().token(TOKEN).build()
    app_tg.add_handler(CommandHandler("start", start))
    app_tg.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app_tg.add_handler(CallbackQueryHandler(button_handler))
    app_tg.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, order_handler))

    # Запускаем Flask и Telegram параллельно
    threading.Thread(target=run_flask).start()
    app_tg.run_polling()

if __name__ == "__main__":
    main()