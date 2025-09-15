import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

TOKEN = os.environ.get("BOT_TOKEN")  # если используешь переменные окружения
WEBHOOK_URL = "https://telegram-bot-80zy.onrender.com"  # твой Render URL

app = Flask(__name__)

# создаём приложение Telegram
application = Application.builder().token(TOKEN).build()

@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok", 200

async def set_webhook():
    await application.bot.set_webhook(f"{WEBHOOK_URL}/webhook/{TOKEN}")

def main():
    # добавляй хендлеры тут (start, text_handler и т.д.)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    application.add_handler(CallbackQueryHandler(button_handler))

    # запускаем Flask
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    import asyncio
    asyncio.run(set_webhook())
    main()