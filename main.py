import random
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# 🔑 তোমার BotFather token এখানে বসাবে
TOKEN = "8999370933:AAGMh6xONhfRHC4-JoEfhst4h31EECZ6zUE"

# 📊 OTC Market list
MARKETS = [
    "USD/PHP (OTC)",
    "USD/ARS (OTC)",
    "USD/BDT (OTC)",
    "USD/CAD (OTC)",
    "AUD/NZD (OTC)",
    "USD/BRL (OTC)",
    "USD/IDR (OTC)",
    "GBP/USD (OTC)",
    "CHF/JPY (OTC)",
    "EUR/AUD (OTC)",
    "NZD/JPY (OTC)",
    "USD/INR (OTC)",
    "EUR/JPY (OTC)",
    "USD/MXN (OTC)"
]

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Welcome to OTC Signal Bot!\n\n👉 লিখুন: live signal"
    )

# live signal command
async def live_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    row = []

    for market in MARKETS:
        row.append(InlineKeyboardButton(market, callback_data=market))

        if len(row) == 2:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "📊 Select OTC Market:",
        reply_markup=reply_markup
    )

# button click handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    market = query.data

    signal = random.choice(["BUY 📈", "SELL 📉"])
    change = round(random.uniform(-2, 2), 2)
    win_rate = random.randint(85, 95)
    time_now = datetime.now().strftime("%H:%M:%S")

    text = f"""
📊 {market}

Signal: {signal}
⏰ Time: {time_now}
📈 Change: {change}%
🏆 Win Rate: {win_rate}%
"""

    await query.edit_message_text(text)

# chat handler
async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if "live signal" in text:
        await live_signal(update, context)
    else:
        await update.message.reply_text("👉 লিখুন: live signal")

# app setup
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("live_signal", live_signal))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_handler))

print("🤖 Bot is running...")
app.run_polling()
