import os
import random
import requests
from threading import Thread
from flask import Flask, request, jsonify

# ==========================================
# 🔑 BOT CONFIGURATION
# ==========================================
TOKEN = "8999370933:AAHsrfWV1sNgX2cFB-7qJGAq6Mi4"
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

# ==========================================
# 🌐 FLASK WEB SERVER & WEBHOOK
# ==========================================
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot is running perfectly via Webhook!"

@app_flask.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        
        if text == "/start":
            send_welcome_menu(chat_id)
            
    elif "callback_query" in data:
        callback_id = data["callback_query"]["id"]
        chat_id = data["callback_query"]["message"]["chat"]["id"]
        message_id = data["callback_query"]["message"]["message_id"]
        callback_data = data["callback_query"]["data"]
        
        requests.post(f"{TELEGRAM_API}/answerCallbackQuery", json={"callback_query_id": callback_id})
        handle_button_click(chat_id, message_id, callback_data)
        
    return jsonify({"status": "success"}), 200

# ==========================================
# 🤖 TELEGRAM BOT FUNCTIONS
# ==========================================
def send_welcome_menu(chat_id):
    payload = {
        "chat_id": chat_id,
        "text": "👋 স্বাগতম! আমি আপনার ট্রেডিং এআই বট।\nনিচের যেকোনো একটি অপশন সিলেক্ট করুন:",
        "reply_markup": {
            "inline_keyboard": [
                [{"text": "📊 মার্কেট অ্যানালাইসিস (Market Analyze)", "callback_data": "market_analyze"}],
                [{"text": "🟢 লাইভ সিগন্যাল (Live Signal)", "callback_data": "live_signal"}],
                [{"text": "⏳ ফিউচার সিগন্যাল (Future Signal)", "callback_data": "future_signal"}]
            ]
        }
    }
    requests.post(f"{TELEGRAM_API}/sendMessage", json=payload)

def handle_button_click(chat_id, message_id, callback_data):
    MARKETS = ["USD/PHP (OTC)", "USD/ARS (OTC)", "USD/BDT (OTC)", "AUD/NZD (OTC)", "USD/BRL (OTC)"]
    
    if callback_data == 'market_analyze':
        response_text = "📊 **মার্কেট অ্যানালাইসিস রিপোর্ট:**\n\nবর্তমান মার্কেট ট্রেন্ড আপওয়ার্ড (Upward)। আরএসআই (RSI) লেভেল স্বাভাবিক আছে।"
    elif callback_data == 'live_signal':
        market = random.choice(MARKETS)
        direction = random.choice(["🟢 CALL (BUY)", "🔴 PUT (SELL)"])
        response_text = (
            "🟢 **লাইভ ট্রেডিং সিগন্যাল**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 মার্কেট: {market}\n"
            f"👉 ডিরেকশন: {direction}\n"
            f"⏳ টাইমফ্রেম: 1 MIN\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "⚠️ *নিজ দায়িত্বে সঠিক সময়ে এন্ট্রি নিন!*"
        )
    elif callback_data == 'future_signal':
        response_text = "⏳ **ফিউচার সিগন্যাল (Upcoming):**\n\nNext Entry: 15-30 mins\nAsset: BTC/USDT\nDirection: BUY"
    else:
        return

    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": response_text,
        "parse_mode": "Markdown"
    }
    requests.post(f"{TELEGRAM_API}/editMessageText", json=payload)

def set_webhook():
    render_url = os.environ.get("RENDER_EXTERNAL_URL")
    if render_url:
        webhook_url = f"{render_url}/webhook"
        requests.post(f"{TELEGRAM_API}/setWebhook", json={"url": webhook_url})
        print(f"🚀 Webhook successfully set to: {webhook_url}")

if __name__ == "__main__":
    Thread(target=set_webhook).start()
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)
