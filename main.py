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
# ==========================================
# 📊 SIGNAL TRACKER & GLOBAL CONTROL
# ==========================================
signal_stats = {
    "total": 12,
    "profit": 10,
    "loss": 2
}

last_chat_id = None
timer_started = False  # টাইমার যেন বারবার চালু না হয়

# ==========================================
# 🤖 TELEGRAM BOT MULTI-MENU FUNCTIONS
# ==========================================

# ১. স্টার্ট কমান্ড ফাংশন (যা ৩টি বাটন দেখাবে)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_chat_id, timer_started
    last_chat_id = update.effective_chat.id
    
    # ইউজার প্রথমবার স্টার্ট দিলে ব্যাকগ্রাউন্ডে অটো-রিপোর্ট লুপ চালু হবে (কোনো ক্র্যাশ ছাড়া)
    if not timer_started:
        context.application.create_task(auto_report_loop(context))
        timer_started = True

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
    analysis_text = "📊 **মার্কেট অ্যানালাইসিস রিপোর্ট:**\n\nবর্তমান মার্কেট ট্রেন্ড আপওয়ার্ড (Upward)। আরএসআই (RSI) লেভেল স্বাভাবিক আছে।"
    await query.edit_message_text(text=analysis_text, parse_mode='Markdown')

# ৩. ফিউচার সিগন্যালের ফাংশন
async def future_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    future_text = "⏳ **ফিউচার সিগন্যাল (Upcoming):**\n\nNext Entry: 15-30 mins\nAsset: BTC/USDT\nDirection: BUY"
    await query.edit_message_text(text=future_text, parse_mode='Markdown')

# ৪. বাটন ক্লিকের রেসপন্স হ্যান্ডলার
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'market_analyze':
        await market_analyze(update, context)
    elif query.data == 'live_signal':
        await live_signal(update, context)
    elif query.data == 'future_signal':
        await future_signal(update, context)

# ৫. নিরাপদ ও অফিশিয়াল নিয়মে ১৫ মিনিট পর পর অটো রিপোর্ট পাঠানোর লুপ
async def auto_report_loop(context: ContextTypes.DEFAULT_TYPE):
    import asyncio
    while True:
        await asyncio.sleep(900)  # ৯০০ সেকেন্ড = ১৫ মিনিট পর পর চলবে
        if last_chat_id:
            total = signal_stats["total"]
            profit = signal_stats["profit"]
            loss = signal_stats["loss"]
            win_rate = (profit / total) * 100 if total > 0 else 0
            
            report_text = (
                "📊 **ট্রেডিং রেজাল্ট আপডেট (প্রতি ১৫ মিনিট পর পর)**\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f" মোট সিগন্যাল: {total} টি\n"
                f"🟢 প্রফিট (Win): {profit} টি ✅\n"
                f"🔴 লস (Loss): {loss} টি ❌\n"
                f"🏆 উইনিং রেট (Win Rate): {win_rate:.1f}%\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "📈 *সঠিক সময়ে এন্ট্রি নিয়ে প্রফিট বুক করুন!*"
            )
            try:
                await context.bot.send_message(chat_id=last_chat_id, text=report_text, parse_mode='Markdown')
                print("⏰ 15-minute report sent successfully via asyncio task!")
            except Exception as e:
                print(f"Error sending automatic report: {e}")

# বট বিল্ড করা
telegram_app = ApplicationBuilder().token(TOKEN).build()

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(button_handler))

# ==========================================
# 🌐 MAIN & WEB SERVER START
# ==========================================
if __name__ == "__main__":
    import os
    from threading import Thread
    
    port = int(os.environ.get("PORT", 10000))
    
    # Flask সার্ভার ব্যাকগ্রাউন্ডে চালু রাখা (Render-এর পোর্ট সচল রাখার জন্য)
    def start_flask():
        app_flask.run(host="0.0.0.0", port=port)
    Thread(target=start_flask, daemon=True).start()
    
    print("🤖 Bot & Web Server are running smoothly without conflicts...")
    telegram_app.run_polling()
