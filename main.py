import random
import threading
from datetime import datetime
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# =========================
# 🔑 BOT TOKEN
# =========================
TOKEN="8999370933:AAHsrfWVlsNgX2cFB-7qJGAq6Mi4CF6qVF8"

# =========================
# 🌐 FLASK SERVER
# =========================
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot is running!"

def run_web():
    app_flask.run(host="0.0.0.0", port=10000)

# =========================
# 📊 OTC MARKETS
# =========================
MARKETS = [
    "USD/PHP (OTC)", "USD/ARS (OTC)", "USD/BDT (OTC)", "USD/CAD (OTC)",
    "AUD/NZD (OTC)", "USD/BRL (OTC)", "USD/IDR (OTC)", "GBP/USD (OTC)",
    "CHF/JPY (OTC)", "EUR/AUD (OTC)", "NZD/JPY (OTC)", "USD/INR (OTC)",
    "EUR/JPY (OTC)", "USD/MXN (OTC)"
]

# =========================
# 🚀 START COMMAND
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Welcome to OTC Signal Bot!\n\n👉 লিখুন: live signal")

# =========================
# 📊 LIVE SIGNAL
# =========================
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
    await update.message.reply_text("📊 Select OTC Market:", reply_markup=reply_markup)

# =========================
# 🔘 BUTTON CLICK
# =========================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    market = query.data
    signal = random.choice(["BUY 📈", "SELL 📉"])
    change = round(random.uniform(-2, 2), 2)
    win_rate = random.randint(85, 95)
    time_now = datetime.now().strftime("%H:%M:%S")
    
    text = f'''
📊 {market}
Signal: {signal}
⏰ Time: {time_now}
📈 Change: {change}%
🏆 Win Rate: {win_rate}%
'''
    await query.edit_message_text(text)

# =========================
# 💬 CHAT MODE
# =========================
async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if "live signal" in text:
        await live_signal(update, context)
    else:
        await update.message.reply_text("👉 লিখুন: live signal")

# =========================
# 🤖 TELEGRAM BOT
# =========================
telegram_app = ApplicationBuilder().token(TOKEN).build()
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("live_signal", live_signal))
telegram_app.add_handler(CallbackQueryHandler(button_handler))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_handler))

# =========================
# ▶️ MAIN
# =========================
if __name__ == "__main__":
    import os
    from threading import Thread
    
    # Render-এর পোর্ট সেট করা
    port = int(os.environ.get("PORT", 10000))
    
    # Flask রান করার জন্য থ্রেড চালু করা
    def start_flask():
        app_flask.run(host="0.0.0.0", port=port)
        
    Thread(target=start_flask).start()
    print("🤖 Bot & Web Server are running...")
    
    # Telegram polling চালু করা
    telegram_app.run_polling()
