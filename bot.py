import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

# 🔑 Токен
TOKEN = os.environ.get("BOT_TOKEN")

# 🌍 Render URL
WEBHOOK_URL = "https://telegram-bot-80zy.onrender.com"

# 🛠 Админ ID
ADMIN_ID = 437753009

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
        user_data[user_id]["waiting_name"] = True


async def name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id in user_data and user_data[user_id].get("waiting_name"):
        name = update.message.text
        problem = user_data[user_id].get("problem", "Не указана")

        # Подтверждение клиенту
        await update.message.reply_text(
            f"✅ Спасибо, {name}! Ваша заявка принята. Скоро мы свяжемся с вами."
        )

        # Заявка админу
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

        user_data[user_id] = {}


def main():
    # Регистрируем хендлеры
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, name_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    application.add_handler(CallbackQueryHandler(button_handler))

    # Запускаем webhook
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        url_path=TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{TOKEN}"
    )


if __name__ == "__main__":
    main()