import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

TOKEN = os.getenv("BOT_TOKEN")

# /start: показать меню
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

# обработка нажатий по кнопкам «О нас» / «Помощь»
async def button_handler(update, context):
    query = update.callback_query
    await query.answer()
    if query.data == "about":
        await query.edit_message_text(
            "📢 **RemPlus — сервис по ремонту техники**\n\n"
            "🔧 Ремонт смартфонов, планшетов и ноутбуков\n"
            "📍 Адрес: г. Нижний Тагил, ул. Циолковского, д.39\n"
            "☎️ Телефон: +7 912 210-00-96\n"
            "🕙 Режим работы: ежедневно с 10:00 до 19:00\n\n"
            "Гарантия качества и честный сервис ✅"
        )
    elif query.data == "help":
        await query.edit_message_text(
            "🛠 Доступные команды:\n"
            "/start — открыть меню\n"
            "/about — информация о сервисе\n"
            "/help — список команд\n\n"
            "Чтобы связаться с мастером, нажмите кнопку «Связаться» ниже ⬇️"
        )

# запуск приложения
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.run_polling()