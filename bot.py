import os
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# 🔑 Твой токен
TOKEN = "8238890929:AAG3tnUSJc4YY4xyZQJXeRNWEQPUW4rg2VM"

# ID админа
ADMIN_ID = 437753009

# Для хранения состояния диалога
user_data = {}

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# 🚀 Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_data[user_id] = {}
    await update.message.reply_text(
        "Привет! 👋 Я бот сервиса РемПлюс.\n\n📱 Напишите марку и модель устройства."
    )
    user_data[user_id]["step"] = "waiting_model"


# 📝 Обработка текста
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()

    # Ожидаем модель
    if user_data.get(user_id, {}).get("step") == "waiting_model":
        user_data[user_id]["model"] = text
        user_data[user_id]["step"] = "waiting_problem"
        await update.message.reply_text(
            "✍️ Отлично! Теперь напишите проблему (например: «не заряжается», «разбит экран»)."
        )
        return

    # Ожидаем проблему
    if user_data.get(user_id, {}).get("step") == "waiting_problem":
        user_data[user_id]["problem"] = text
        problem = text.lower()

        if "экран" in problem or "дисплей" in problem:
            await update.message.reply_text(
                "💡 Замена экрана — от 3000 ₽, срок 1 день.\nХотите записаться?",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🛒 Записаться", callback_data="order")]]
                ),
            )
        elif "заряд" in problem or "разъем" in problem or "не заряжается" in problem:
            await update.message.reply_text(
                "🔌 Замена разъёма зарядки — от 2000 ₽, срок 1 день.\nХотите записаться?",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🛒 Записаться", callback_data="order")]]
                ),
            )
        else:
            await update.message.reply_text(
                "🔎 Бесплатная диагностика вашего устройства.\nХотите записаться?",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🛒 Записаться", callback_data="order")]]
                ),
            )

        user_data[user_id]["step"] = "done"
        return


# 🛒 Кнопка «Записаться»
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    name = query.from_user.first_name
    model = user_data.get(user_id, {}).get("model", "Не указано")
    problem = user_data.get(user_id, {}).get("problem", "Не указано")

    # Отправляем пользователю
    await query.edit_message_text("✅ Ваша заявка принята! Мы свяжемся с вами 📞")

    # Уведомляем админа
    msg = f"📩 Новая заявка:\n👤 {name}\n📱 {model}\n❌ {problem}"
    await context.bot.send_message(chat_id=ADMIN_ID, text=msg)


# 🚀 Основной запуск
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.add_handler(CallbackQueryHandler(button_handler))

    port = int(os.environ.get("PORT", 10000))
    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=TOKEN,
        webhook_url=f"https://telegram-bot-80zy.onrender.com/{TOKEN}"
    )


if __name__ == "__main__":
    main()