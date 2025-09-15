import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

TOKEN = os.getenv("BOT_TOKEN")

# --- Команда /start ---
async def start(update, context):
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
    await update.message.reply_text("Привет! 👋 Выбери действие:", reply_markup=reply_markup)

# --- Обработка нажатий ---
async def button_handler(update, context):
    query = update.callback_query
    await query.answer()
    if query.data == "about":
        await query.edit_message_text(
            "📢 Сервис **РемПлюс**\n\n"
            "🔧 Ремонт смартфонов, планшетов и ноутбуков\n"
            "📍 Адрес: г. Нижний Тагил, ул. Циолковского, д.39\n"
            "☎️ Телефон: +7 912 041 21 21\n"
            "🕙 Режим работы: ежедневно с 10:00 до 19:00\n\n"
            "Гарантия качества и честный сервис ✅"
        )
    elif query.data == "help":
        await query.edit_message_text(
            "🛠 Доступные команды:\n"
            "/start — открыть меню\n"
            "/about — информация о РемПлюс\n"
            "/help — список команд\n\n"
            "☎️ Для связи звоните: +7 912 041 21 21\n"
            "или нажмите кнопку «Связаться» ниже ⬇️"
        )

# --- Запуск ---
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.run_polling()