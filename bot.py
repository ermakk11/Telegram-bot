import os
from flask import Flask, request
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
    ContextTypes,
    filters
)

# === Настройки ===
TOKEN = os.getenv("BOT_TOKEN")
OWNER_LINK = "https://t.me/ermakov_remont"
ADMIN_ID = 437753009
USER_CONTEXT = {}

# URL твоего сервиса на Render
# Например: https://telegram-bot-8ozy.onrender.com
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# === Flask для webhook ===
app = Flask(__name__)
telegram_app = Application.builder().token(TOKEN).build()


@app.route("/")
def home():
    return "✅ Bot is running with Webhook!"


@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    """Получение апдейтов от Telegram"""
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    telegram_app.update_queue.put_nowait(update)
    return "ok"


# === Команда /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["О нас", "Помощь", "Связаться"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Привет! 👋 Я бот сервиса РемПлюс.\n"
        "📱 Напишите марку и модель устройства, а также проблему.",
        reply_markup=reply_markup
    )


# === Универсальный обработчик текста ===
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()
    text_lower = text.lower()

    # --- Если пользователь в процессе заявки ---
    if user_id in USER_CONTEXT and "stage" in USER_CONTEXT[user_id]:
        stage = USER_CONTEXT[user_id]["stage"]

        if stage == "name":
            USER_CONTEXT[user_id]["name"] = text
            USER_CONTEXT[user_id]["stage"] = "phone"
            await update.message.reply_text("📞 Укажите ваш номер телефона:")
            return

        elif stage == "phone":
            USER_CONTEXT[user_id]["phone"] = text
            name = USER_CONTEXT[user_id].get("name")
            phone = USER_CONTEXT[user_id].get("phone")
            problem = USER_CONTEXT[user_id].get("problem")

            username = (
                f"@{update.message.from_user.username}"
                if update.message.from_user.username
                else "—"
            )

            card = (
                f"🆕 <b>Новая заявка</b>\n\n"
                f"👤 Имя: <b>{name}</b>\n"
                f"📞 Телефон: <b>{phone}</b>\n"
                f"📱 Проблема: <b>{problem}</b>\n"
                f"🌐 Username: {username}"
            )

            keyboard = InlineKeyboardMarkup(
                [[InlineKeyboardButton("📩 Позвонить", url=f"tel:{phone}")]]
            )

            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=card,
                parse_mode="HTML",
                reply_markup=keyboard
            )

            await update.message.reply_text("✅ Спасибо! Ваша заявка принята, мы скоро свяжемся с вами.")
            USER_CONTEXT[user_id] = {}  # очистка
            return

    # --- Если это обычное сообщение (новая проблема) ---
    if "о нас" in text_lower:
        await update.message.reply_text("👨‍🔧 РемПлюс — профессиональный ремонт смартфонов.\nТелефон: +79120412121")
        return
    if "помощь" in text_lower:
        await update.message.reply_text("❓ Просто напишите модель телефона и проблему (например: «iPhone 12 экран»).")
        return
    if "связаться" in text_lower:
        await update.message.reply_text(f"📞 Напишите нам: {OWNER_LINK}")
        return

    # Сохраняем проблему
    USER_CONTEXT[user_id] = {"problem": text}

    # Определяем услугу
    if "экран" in text_lower or "дисплей" in text_lower:
        reply = f"💡 Замена экрана — от 7000 ₽, срок 1 день.\n🛠 Хотите записаться на ремонт?"
    elif "заряд" in text_lower or "разъем" in text_lower or "порт" in text_lower or "не заряжается" in text_lower:
        reply = f"🔌 Замена разъёма зарядки — от 2000 ₽, срок 1 день.\n🛠 Хотите записаться на ремонт?"
    else:
        reply = f"🔍 Бесплатная диагностика вашего устройства.\n🛠 Хотите записаться?"

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🛒 Записаться", callback_data="order")]])
    await update.message.reply_text(reply, reply_markup=keyboard)


# === Inline-кнопки ===
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "order":
        USER_CONTEXT[query.from_user.id]["stage"] = "name"
        await query.message.reply_text("✍️ Отлично! Как вас зовут?")


# === Запуск ===
def main():
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    telegram_app.add_handler(CallbackQueryHandler(button_handler))

    # Устанавливаем webhook
    import asyncio
    async def set_webhook():
        await telegram_app.bot.set_webhook(f"{WEBHOOK_URL}/webhook/{TOKEN}")

    asyncio.get_event_loop().run_until_complete(set_webhook())


if __name__ == "__main__":
    main()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))