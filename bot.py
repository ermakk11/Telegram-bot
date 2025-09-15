import os
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

# === Flask-заглушка для Render ===
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Bot is running on Render!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# === Настройки ===
TOKEN = os.getenv("BOT_TOKEN")
OWNER_LINK = "https://t.me/ermakov_remont"
ADMIN_ID = 437753009
USER_CONTEXT = {}

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

            card = (
                f"🆕 <b>Новая заявка</b>\n\n"
                f"👤 Имя: <b>{name}</b>\n"
                f"📞 Телефон: <b>{phone}</b>\n"
                f"📱 Проблема: <b>{problem}</b>"
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
    app_tg = Application.builder().token(TOKEN).build()
    app_tg.add_handler(CommandHandler("start", start))
    app_tg.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app_tg.add_handler(CallbackQueryHandler(button_handler))

    threading.Thread(target=run_flask).start()
    app_tg.run_polling()

if __name__ == "__main__":
    main()