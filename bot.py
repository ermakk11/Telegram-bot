import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ConversationHandler, ContextTypes
)

TOKEN = os.getenv("BOT_TOKEN")

# твой Telegram ID (куда будут приходить заявки)
ADMIN_ID = 437753009

# --- Состояния диалога ---
ASK_NAME, ASK_PHONE, ASK_PROBLEM = range(3)

# --- Команда /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("ℹ️ О нас", callback_data="about"),
            InlineKeyboardButton("❓ Помощь", callback_data="help")
        ],
        [
            InlineKeyboardButton("📞 Связаться", url="https://t.me/ermakov_remont")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привет! 👋 Я бот сервиса РемПлюс.\nЗадай вопрос или выбери действие:", reply_markup=reply_markup)

# --- Обработка кнопок ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "about":
        await query.edit_message_text(
            "📢 Сервис **РемПлюс**\n\n"
            "🔧 Ремонт смартфонов, планшетов и ноутбуков\n"
            "📍 Адрес: г. Нижний Тагил, ул. Циолковского, д.39\n"
            "☎️ Телефон: +7 912 041 21 21\n"
            "🕙 Работаем ежедневно с 10:00 до 19:00\n\n"
            "Гарантия качества ✅"
        )
    elif query.data == "help":
        await query.edit_message_text(
            "🛠 Доступные команды:\n"
            "/start — открыть меню\n"
            "/about — информация о РемПлюс\n"
            "/help — список команд\n\n"
            "📞 Для связи: +7 912 041 21 21"
        )
    elif query.data == "buy":
        await query.edit_message_text("✍️ Давайте оформим заявку.\nКак вас зовут?")
        return ASK_NAME

# --- Сбор заявки ---
async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("📱 Укажите ваш номер телефона:")
    return ASK_PHONE

async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("🔧 Опишите, что случилось с устройством:")
    return ASK_PROBLEM

async def ask_problem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["problem"] = update.message.text

    name = context.user_data["name"]
    phone = context.user_data["phone"]
    problem = context.user_data["problem"]

    # отправляем админу
    text = (
        f"📩 Новая заявка:\n\n"
        f"👤 Имя: {name}\n"
        f"📱 Телефон: {phone}\n"
        f"🔧 Проблема: {problem}"
    )
    await context.bot.send_message(chat_id=ADMIN_ID, text=text)

    # подтверждение клиенту
    await update.message.reply_text("✅ Спасибо! Ваша заявка принята. Мы свяжемся с вами в ближайшее время.")

    return ConversationHandler.END

# --- Отмена заявки ---
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Заявка отменена.")
    return ConversationHandler.END

# --- FAQ ответы ---
FAQ = {
    "экран": "💡 Замена экрана iPhone 12 — от 7000₽, срок 1 день.",
    "батаре": "🔋 Замена аккумулятора — от 2500₽, срок 1 день.",
    "вода": "💦 Чистка после попадания жидкости — от 2000₽.",
    "адрес": "📍 Мы находимся: Нижний Тагил, ул. Циолковского, д.39",
    "телефон": "☎️ Наш телефон: +7 912 041 21 21",
    "время": "🕙 Работаем ежедневно с 10:00 до 19:00"
}

async def faq_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    for key, answer in FAQ.items():
        if key in text:
            keyboard = [[InlineKeyboardButton("🛒 Оформить заявку", callback_data="buy")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(f"{answer}\n\nХотите оформить заявку прямо сейчас?", reply_markup=reply_markup)
            return
    await update.message.reply_text("🤔 Я пока не знаю ответа на это. Попробуйте написать про «экран», «батарея», «адрес» или «телефон».")

# --- Запуск ---
app = Application.builder().token(TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(button_handler, pattern="^buy$")],
    states={
        ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
        ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
        ASK_PROBLEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_problem)],
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(conv_handler)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, faq_handler))

app.run_polling()