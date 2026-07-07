import os
import random
import requests
import time
from datetime import datetime
from threading import Thread
from flask import Flask, request, jsonify

TOKEN = "8999370933:AAEC1aGgpIyE1C1kDJNB_Mu5t25BSyEDQ30"
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

app_flask = Flask(__name__)

# সেশন ডাটা স্টোর
active_sessions = {}

@app_flask.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text")
        
        if text == "/start":
            active_sessions[chat_id] = {"start_time": datetime.now(), "trades": 0, "wins": 0, "losses": 0}
            send_welcome_menu(chat_id)
        elif text == "/stop":
            send_final_report(chat_id)
            if chat_id in active_sessions: del active_sessions[chat_id]
            
    elif "callback_query" in data:
        handle_callback(data)
    return jsonify({"status": "success"}), 200

def get_next_candle_time():
    now = datetime.now()
    next_minute = now.minute + 1
    return f"{now.hour}:{next_minute:02d}"

def send_welcome_menu(chat_id):
    payload = {
        "chat_id": chat_id,
        "text": "🟢 **সেশন শুরু হয়েছে!** ট্রেডিংয়ের জন্য নিচের অপশন সিলেক্ট করুন:",
        "reply_markup": {"inline_keyboard": [[{"text": "🟢 লাইভ সিগন্যাল", "callback_data": "main_live"}], [{"text": "⏳ ফিউচার সিগন্যাল", "callback_data": "main_future"}], [{"text": "📊 অ্যানালাইসিস", "callback_data": "main_analyze"}]]}
    }
    requests.post(f"{TELEGRAM_API}/sendMessage", json=payload)

def handle_callback(data):
    chat_id = data["callback_query"]["message"]["chat"]["id"]
    callback_data = data["callback_query"]["data"]
    
    if callback_data.startswith(("lv_", "ft_")):
        # সিগন্যাল লজিক
        pair = callback_data.split("_", 1)[1]
        s_type = "LIVE" if callback_data.startswith("lv_") else "FUTURE"
        
        # রেজাল্ট আপডেট
        if chat_id in active_sessions:
            active_sessions[chat_id]["trades"] += 1
            if random.random() > 0.2: # ৮০% উইনরেট সিমুলেশন
                active_sessions[chat_id]["wins"] += 1
                res = "✅ PROFIT"
            else:
                active_sessions[chat_id]["losses"] += 1
                res = "❌ LOSS"
        
        msg = (f"🎯 **QUOTEX SIGNAL**\nমার্কেট: {pair}\nটাইম: {get_next_candle_time()} এর জন্য\nফলাফল: {res}\n\nসেশন ট্রেড: {active_sessions[chat_id]['trades']}")
        requests.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": msg})

def send_final_report(chat_id):
    if chat_id in active_sessions:
        s = active_sessions[chat_id]
        duration = datetime.now() - s["start_time"]
        msg = (f"🛑 **সেশন সমাপ্ত!**\n\n⏰ সময়কাল: {str(duration).split('.')[0]}\n📈 মোট ট্রেড: {s['trades']}\n✅ প্রফিট: {s['wins']}\n❌ লস: {s['losses']}")
        requests.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": msg})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)
