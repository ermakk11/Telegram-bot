from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import os

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

    await update.message.reply_text("Привет! 👋 Отправь мне фото, и я дам его File ID.\nА потом напиши /start, чтобы открыть меню.", reply_markup=reply_markup)

# --- Обработка нажатий ---
async def button_handler(update, context):
    query = update.callback_query
    await query.answer()

    if query.data == "about":
        await query.edit_message_text("📢 Я бот, созданный на Python и работающий на Render 🚀")
    elif query.data == "help":
        await query.edit_message_text("🛠 Доступные команды:\n/start — меню\n/about — о боте\n/help — помощь")

# --- Временный обработчик для получения File ID ---
async def get_file_id(update, context):
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        await update.message.reply_text(f"File ID этого изображения:\n{file_id}")

# --- Запуск ---
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.PHOTO, get_file_id))  # <-- добавили сюда

app.run_polling()