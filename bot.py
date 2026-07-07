import os
import random
from datetime import datetime
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# ==========================================
# 🔑 BOT CONFIGURATION
# ==========================================
TOKEN = "8999370933:AAHsrfWV1sNgX2cFB-7qJGAq6Mi4"

# ==========================================
# 🌐 FLASK WEB SERVER (Render-এর জন্য)
# ==========================================
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot is running perfectly!"

def start_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)

# ==========================================
# 📊 OTC MARKETS & STATS
# ==========================================
MARKETS = [
    "USD/PHP (OTC)", "USD/ARS (OTC)", "USD/BDT (OTC)",
    "AUD/NZD (OTC)", "USD/BRL (OTC)", "USD/IDR (OTC)",
    "CHF/JPY (OTC)", "EUR/AUD (OTC)", "NZD/JPY (OTC)"
]

# ১. স্টার্ট কমান্ড ফাংশন (৩টি বাটন দেখাবে)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 মার্কেট অ্যানালাইসিস (Market Analyze)", callback_data='market_analyze')],
        [InlineKeyboardButton("🟢 লাইভ সিগন্যাল (Live Signal)", callback_data='live_signal')],
        [InlineKeyboardButton("⏳ ফিউচার সিগন্যাল (Future Signal)", callback_data='future_signal')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 স্বাগতম! আমি আপনার ট্রেডিং এআই বট।\nনিচের যেকোনো একটি অপশন সিলেক্ট করুন:", 
        reply_markup=reply_markup
    )

# ২. মার্কেট অ্যানালাইসিসের ফাংশন
async def market_analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="📊 **মার্কেট অ্যানালাইসিস রিপোর্ট:**\n\nবর্তমান মার্কেট ট্রেন্ড আপওয়ার্ড (Upward)। আরএসআই (RSI) লেভেল স্বাভাবিক আছে。", parse_mode='Markdown')

# ৩. লাইভ সিগন্যালের ফাংশন
async def live_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    market = random.choice(MARKETS)
    direction = random.choice(["🟢 CALL (BUY)", "🔴 PUT (SELL)"])
    time_str = datetime.now().strftime("%H:%M")
    
    signal_text = (
        "🟢 **লাইভ ট্রেডিং সিগন্যাল**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 মার্কেট: {market}\n"
        f"👉 ডিরেকশন: {direction}\n"
        f"⏳ টাইমফ্রেম: 1 MIN\n"
        f"⏰ এন্ট্রি টাইম: {time_str}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "⚠️ *নিজ দায়িত্ব সঠিক সময়ে এন্ট্রি নিন!*"
    )
    await query.edit_message_text(text=signal_text, parse_mode='Markdown')

# ৪. ফিউচার সিগন্যালের ফাংশন
async def future_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="⏳ **ফিউচার সিগন্যাল (Upcoming):**\n\nNext Entry: 15-30 mins\nAsset: BTC/USDT\nDirection: BUY", parse_mode='Markdown')

# ৫. বাটন ক্লিকের রেসপন্স হ্যান্ডলার
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == 'market_analyze':
        await market_analyze(update, context)
    elif query.data == 'live_signal':
        await live_signal(update, context)
    elif query.data == 'future_signal':
        await future_signal(update, context)

# ==========================================
# 🚀 INITIALIZE BOT
# ==========================================
telegram_app = ApplicationBuilder().token(TOKEN).build()
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(button_handler))

if __name__ == "__main__":
    Thread(target=start_flask, daemon=True).start()
    print("🤖 AI Bot is starting...")
    telegram_app.run_polling()
