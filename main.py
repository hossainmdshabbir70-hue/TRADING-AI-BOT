import os
import random
import asyncio
from datetime import datetime
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# ==========================================
# 🔑 BOT CONFIGURATION
# ==========================================
TOKEN = "8999370933:AAHsrfWV1sNgX2cFB-7qJGAq6Mi4"  # আপনার বটের টোকেন এখানে পারফেক্টলি আছে

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
    "CHF/JPY (OTC)", "EUR/AUD (OTC)", "NZD/JPY (OTC)",
    "EUR/JPY (OTC)", "USD/MXN (OTC)"
]

signal_stats = {
    "total": 12,
    "profit": 10,
    "loss": 2
}

last_chat_id = None
timer_started = False

# ==========================================
# 🤖 TELEGRAM BOT FUNCTIONS
# ==========================================

# ১. স্টার্ট কমান্ড ফাংশন (৩টি বাটন দেখাবে)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_chat_id, timer_started
    last_chat_id = update.effective_chat.id
    
    # ব্যাকগ্রাউন্ডে অটো-রিপোর্ট লুপ চালু করা
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

# ৩. লাইভ সিগন্যালের ফাংশন
async def live_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
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
        "⚠️ *নিজ দায়িত্বে সঠিক সময়ে এন্ট্রি নিন!*"
    )
    await query.edit_message_text(text=signal_text, parse_mode='Markdown')

# ৪. ফিউচার সিগন্যালের ফাংশн
async def future_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    future_text = "⏳ **ফিউচার সিগন্যাল (Upcoming):**\n\nNext Entry: 15-30 mins\nAsset: BTC/USDT\nDirection: BUY"
    await query.edit_message_text(text=future_text, parse_mode='Markdown')

# ৫. বাটন ক্লিকের রেসপন্স হ্যান্ডলার
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'market_analyze':
        await market_analyze(update, context)
    elif query.data == 'live_signal':
        await live_signal(update, context)
    elif query.data == 'future_signal':
        await future_signal(update, context)

# ৬. ১৫ মিনিট পর পর অটো রিপোর্ট পাঠানোর নিরাপদ লুপ
async def auto_report_loop(context: ContextTypes.DEFAULT_TYPE):
    while True:
        await asyncio.sleep(900)  # ১৫ মিনিট পর পর চলবে
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
            except Exception as e:
                print(f"Error sending automatic report: {e}")

# ==========================================
# 🚀 INITIALIZE & START BOT
# ==========================================
telegram_app = ApplicationBuilder().token(TOKEN).build()

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(button_handler))

if __name__ == "__main__":
    # Flask সার্ভার ব্যাকগ্রাউন্ডে চালু করা
    Thread(target=start_flask, daemon=True).start()
    
    # টেলিগ্রাম বট লাইভ করা
    print("🤖 Trading AI Bot is starting...")
    telegram_app.run_polling()
