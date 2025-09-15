import os
import asyncio
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

# 🔑 Токен
TOKEN = os.environ.get("BOT_TOKEN")

# 🌍 Render URL
WEBHOOK_URL = "https://telegram-bot-80zy.onrender.com"

# 🛠 Админ ID (твой)
ADMIN_ID = 437753009

# Flask-приложение
app = Flask(__name__)

# Telegram приложение
application = Application.builder().token(TOKEN).build()

# === Хранилище состояния клиентов ===
user_data = {}


# === Хендлеры ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! 👋 Я бот сервиса РемПлюс.\n\n"
        "📱 Напишите марку и модель устройства, а также проблему."
    )


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.lower()

    # Сохраняем проблему
    user_data[user_id] = {"problem": update.message.text}

    if "экран" in text or "дисплей" in text:
        await update.message.reply_text(
            "💡 Замена экрана — от 3000 ₽, срок 1 день.\n🔧 Хотите записаться на ремонт?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🛒 Записаться", callback_data="order")]
            ])
        )

    elif "заряд" in text or "разъем" in text or "не заряжается" in text:
        await update.message.reply_text(
            "🔌 Замена разъёма зарядки — от 2000 ₽, срок 1 день.\n🔧 Хотите записаться на ремонт?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🛒 Записаться", callback_data="order")]
            ])
        )

    else:
        await update.message.reply_text(
            "🔎 Бесплатная диагностика вашего устройства.\n🔧 Хотите записаться?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🛒 Записаться", callback_data="order")]
            ])
        )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "order":
        await query.message.reply_text("✍️ Отлично! Как вас зовут?")
        # Меняем состояние
        user_data[user_id]["waiting_name"] = True


async def name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id in user_data and user_data[user_id].get("waiting_name"):
        name = update.message.text
        problem = user_data[user_id].get("problem", "Не указана")

        # Отправляем клиенту подтверждение
        await update.message.reply_text(
            f"✅ Спасибо, {name}! Ваша заявка принята. Скоро мы свяжемся с вами."
        )

        # Отправляем администратору карточку клиента
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                "📩 *Новая заявка!*\n\n"
                f"👤 Имя: {name}\n"
                f"📱 Проблема: {problem}\n"
                f"🆔 Telegram ID: {user_id}"
            ),
            parse_mode="Markdown"
        )

        # Очищаем данные
        user_data[user_id] = {}


# === Webhook обработчик ===
@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok", 200


# === Установка webhook ===
async def set_webhook():
    await application.bot.set_webhook(f"{WEBHOOK_URL}/webhook/{TOKEN}")


def main():
    # Регистрируем хендлеры
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, name_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    application.add_handler(CallbackQueryHandler(button_handler))

    # Запускаем Flask
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))


if __name__ == "__main__":
    asyncio.run(set_webhook())
    main()