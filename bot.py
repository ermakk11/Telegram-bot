import json
import math
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# === Загружаем справочник разъёмов ===
with open("connectors.json", encoding="utf-8") as f:
    CONNECTORS = json.load(f)

# === Твой токен ===
import os
TOKEN = os.getenv("BOT_TOKEN")
OWNER_LINK = "https://t.me/ermakov_remont"

# === Правила ценообразования ===
def round_up_to_100(x):
    return int(math.ceil(x / 100.0)) * 100

def calculate_price(model: str, repair_type: str) -> str:
    model_lower = model.lower()
    connector = None
    for key, conn in CONNECTORS.items():
        if key.lower() in model_lower:
            connector = conn
            break

    if not connector and "iphone" in model_lower:
        connector = "Lightning"

    if not connector:
        return "❌ Не удалось определить модель или разъём."

    if "экран" in repair_type or "дисплей" in repair_type:
        base_price = 0  # здесь можно подставить цену детали с GreenSpark
        total = round_up_to_100(base_price + 3000)
        return f"💡 Замена дисплея для {model}: {total} ₽"

    if "батаре" in repair_type or "аккум" in repair_type:
        if "iphone" in model_lower:
            total = round_up_to_100(2500)
        else:
            total = round_up_to_100(2000)
        return f"🔋 Замена аккумулятора для {model}: {total} ₽"

    if "разъем" in repair_type or "заряд" in repair_type or "порт" in repair_type:
        if connector == "MicroUSB":
            total = round_up_to_100(1200)
        elif connector == "Type-C":
            total = round_up_to_100(2000)
        else:
            total = "По запросу"
        return f"🔌 Замена разъёма ({connector}) для {model}: {total} ₽"

    return f"ℹ️ {model} ({connector}) — уточните, какую услугу рассчитать."

# === Обработчики ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["О нас", "Помощь", "Связаться"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Привет! 👋 Я бот сервиса РемПлюс.\nВыберите действие:", reply_markup=reply_markup)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if "о нас" in text:
        await update.message.reply_text("👨‍🔧 РемПлюс — профессиональный ремонт смартфонов.\nТелефон: +79120412121")
        return
    if "помощь" in text:
        await update.message.reply_text("❓ Вы можете спросить меня о цене ремонта: замена дисплея, аккумулятора, разъёма.")
        return
    if "связаться" in text:
        await update.message.reply_text(f"📞 Напишите нам: {OWNER_LINK}")
        return

    if "замена" in text:
        if "экран" in text or "дисплей" in text:
            service = "экран"
        elif "батаре" in text or "аккум" in text:
            service = "батарея"
        elif "разъем" in text or "заряд" in text or "порт" in text:
            service = "разъем"
        else:
            service = "другое"

        words = update.message.text.split()
        model = " ".join(words[2:]) if len(words) > 2 else update.message.text
        price = calculate_price(model, service)
        await update.message.reply_text(price)
    else:
        await update.message.reply_text("⚡ Напишите, что нужно: замена экрана, батареи или разъёма + модель телефона.")

# === Запуск ===
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.run_polling()

if __name__ == "__main__":
    main()