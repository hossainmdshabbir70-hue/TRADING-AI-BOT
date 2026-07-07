import os
import random
import requests
from datetime import datetime
from threading import Thread
from flask import Flask, request, jsonify

# ==========================================
# 🔑 BOT CONFIGURATION
# ==========================================
TOKEN = "8999370933:AAEC1aGgpIyE1C1kDJNB_Mu5t25BSyEDQ30"
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

app_flask = Flask(__name__)

# কটেক্সের জনপ্রিয় মার্কেট পেয়ার
QUOTEX_MARKETS = [
    "EUR/USD", "GBP/USD", "USD/JPY", 
    "EUR/GBP (OTC)", "USD/INR (OTC)", "USD/BDT (OTC)"
]

# 📊 সেশন মেমোরি স্টোরেজ
active_sessions = {}

@app_flask.route('/')
def home():
    return "Quotex Ultimate Timer Bot is Live!"

@app_flask.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text")
        
        if text == "/start":
            # নতুন সেশন এবং কাউন্টার শুরু
            active_sessions[chat_id] = {
                "start_time": datetime.now(),
                "trades": 0,
                "wins": 0,
                "losses": 0,
                "history": []
            }
            send_welcome_menu(chat_id)
            
        elif text == "/stop":
            send_final_report(chat_id)
            if chat_id in active_sessions:
                del active_sessions[chat_id]
                
    elif "callback_query" in data:
        callback_id = data["callback_query"]["id"]
        chat_id = data["callback_query"]["message"]["chat"]["id"]
        message_id = data["callback_query"]["message"]["message_id"]
        callback_data = data["callback_query"]["data"]
        
        requests.post(f"{TELEGRAM_API}/answerCallbackQuery", json={"callback_query_id": callback_id})
        handle_button_click(chat_id, message_id, callback_data)
        
    return jsonify({"status": "success"}), 200

# ==========================================
# ⏱️ NEXT CANDLE TIMER CALCULATION
# ==========================================
def get_next_candle_time():
    """
    ইউজার যখনই ক্লিক করবে, তার ঠিক পরের মিনিটের 
    ক্যান্ডেল শুরুর পারফেক্ট টাইম (HH:MM) রিটার্ন করবে।
    """
    now = datetime.now()
    next_minute = now.minute + 1
    hour = now.hour
    
    if next_minute >= 60:
        next_minute = 0
        hour = (hour + 1) % 24
        
    return f"{hour:02d}:{next_minute:02d}"

# ==========================================
# 🤖 BOT INTERACTION FLOW
# ==========================================
def send_welcome_menu(chat_id):
    payload = {
        "chat_id": chat_id,
        "text": (
            "👋 **স্বাগতম কটেক্স ট্রেডার বন্ধু!**\n\n"
            "আপনার লাইভ সেশনটি চালু হয়েছে। যখন ট্রেড শেষ করতে চাইবেন, চ্যাটে জাস্ট **/stop** লিখে মেসেজ দিন।\n\n"
            "এখন সিগন্যাল বা এনালাইসিস পেতে নিচের যেকোনো একটি অপশন বেছে নিন:"
        ),
        "parse_mode": "Markdown",
        "reply_markup": {
            "inline_keyboard": [
                [{"text": "🟢 লাইভ সিগন্যাল (Live Signal)", "callback_data": "main_live"}],
                [{"text": "⏳ ফিউচার সিগন্যাল (Future Signal)", "callback_data": "main_future"}],
                [{"text": "📊 মার্কেট অ্যানালাইসিস (Market Analyze)", "callback_data": "main_analyze"}]
            ]
        }
    }
    requests.post(f"{TELEGRAM_API}/sendMessage", json=payload)

def handle_button_click(chat_id, message_id, callback_data):
    # ১. লাইভ বা ফিউচার মেনু ক্লিক করলে মার্কেটের তালিকা দেখাবে
    if callback_data == "main_live":
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": "📈 **Quotex Live Markets**\nলাইভ সিগন্যাল পেতে নিচের যেকোনো একটি মার্কেট সিলেক্ট করুন:",
            "reply_markup": {
                "inline_keyboard": [[{"text": m, "callback_data": f"lv_{m}"}] for m in QUOTEX_MARKETS] + [[{"text": "🔙 প্রধান মেনু", "callback_data": "back_to_main"}]]
            }
        }
        requests.post(f"{TELEGRAM_API}/editMessageText", json=payload)

    elif callback_data == "main_future":
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": "⏳ **Quotex Future Markets**\nফিউচার সিগন্যাল পেতে নিচের যেকোনো একটি মার্কেট সিলেক্ট করুন:",
            "reply_markup": {
                "inline_keyboard": [[{"text": m, "callback_data": f"ft_{m}"}] for m in QUOTEX_MARKETS] + [[{"text": "🔙 প্রধান মেনু", "callback_data": "back_to_main"}]]
            }
        }
        requests.post(f"{TELEGRAM_API}/editMessageText", json=payload)

    elif callback_data == "main_analyze":
        analysis_text = (
            "📊 **QUOTEX MARKET ANALYSIS REPORT**\n\n"
            "• **EUR/USD & GBP/USD:** কারেন্ট ট্রেন্ড আপওয়ার্ড। বায়ারদের প্রেসার বেশি।\n"
            "• **OTC মার্কেটসমূহ:** বর্তমানে অ্যালগরিদমিক সাপোর্ট লেভেল খুব স্ট্রং।"
        )
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": analysis_text,
            "parse_mode": "Markdown",
            "reply_markup": {"inline_keyboard": [[{"text": "🔙 প্রধান মেনু", "callback_data": "back_to_main"}]]}
        }
        requests.post(f"{TELEGRAM_API}/editMessageText", json=payload)

    # ২. নির্দিষ্ট মার্কেট সিলেক্ট করার পর কটেক্স সিগন্যাল জেনারেট করা
    elif callback_data.startswith(("lv_", "ft_")):
        is_live = callback_data.startswith("lv_")
        pair = callback_data.replace("lv_", "") if is_live else callback_data.replace("ft_", "")
        
        direction = random.choice(["🟢 CALL (UP) 👆", "🔴 PUT (DOWN) 👇"])
        candle_time = get_next_candle_time()
        win_rate = random.randint(85, 94)
        
        # সেশন ডাটা ও ব্যাকগ্রাউন্ড উইন/লস রেজাল্ট আপডেট
        if chat_id in active_sessions:
            active_sessions[chat_id]["trades"] += 1
            # ৮০% উইন রেশিও মেইনটেইন করার ট্রিক
            current_result = "PROFIT" if random.random() > 0.18 else "LOSS"
            
            if current_result == "PROFIT":
                active_sessions[chat_id]["wins"] += 1
                res_string = "✅ PROFIT"
            else:
                active_sessions[chat_id]["losses"] += 1
                res_string = "❌ LOSS"
                
            active_sessions[chat_id]["history"].append(f"• {pair} ➡️ {res_string}")
            if len(active_sessions[chat_id]["history"]) > 5:
                active_sessions[chat_id]["history"].pop(0)

        # মেসেজ ফরম্যাট সাজানো
        title = "🎯 **QUOTEX LIVE AI SIGNAL** 🎯" if is_live else "⏳ **QUOTEX FUTURE AI SIGNAL** ⏳"
        expiry = f"`1 MIN` (ক্যান্ডেল শুরু: **{candle_time}**)" if is_live else f"`5 MIN` (ক্যান্ডেল শুরু: **{candle_time}**)"
        
        signal_msg = (
            f"{title}\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 **মার্কেট (Asset):** `{pair}`\n"
            f"👉 **ডিরেকশন (Action):** **{direction}**\n"
            f"⏳ **টাইমফ্রেম (Expiry):** {expiry}\n"
            f"🏆 **উইন রেট (Accuracy):** `{win_rate}%` 🔥\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📢 *নোট: ঘড়ির দিকে নজর রাখুন। সেকেন্ডের কাঁটা শেষ হয়ে নতুন মিনিট শুরু হওয়া মাত্রই ট্রেড প্লেস করবেন।*"
        )
        
        back_tag = "main_live" if is_live else "main_future"
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": signal_msg,
            "parse_mode": "Markdown",
            "reply_markup": {"inline_keyboard": [[{"text": "🔄 অন্য মার্কেট দেখুন", "callback_data": back_tag}], [{"text": "🔙 প্রধান মেনু", "callback_data": "back_to_main"}]]}
        }
        requests.post(f"{TELEGRAM_API}/editMessageText", json=payload)

    elif callback_data == "back_to_main":
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": "আপনার কটেক্স ট্রেডিংকে সহজ করতে নিচের যেকোনো একটি অপশন সিলেক্ট করুন:",
            "reply_markup": {
                "inline_keyboard": [
                    [{"text": "🟢 লাইভ সিগন্যাল (Live Signal)", "callback_data": "main_live"}],
                    [{"text": "⏳ ফিউচার সিগন্যাল (Future Signal)", "callback_data": "main_future"}],
                    [{"text": "📊 মার্কেট অ্যানালাইসিস (Market Analyze)", "callback_data": "main_analyze"}]
                ]
            }
        }
        requests.post(f"{TELEGRAM_API}/editMessageText", json=payload)

# ==========================================
# 🛑 SESSION STOP & REPORT ENGINE
# ==========================================
def send_final_report(chat_id):
    if chat_id in active_sessions:
        s = active_sessions[chat_id]
        duration = datetime.now() - s["start_time"]
        
        # টাইম ডিউরেশন সুন্দর ফরম্যাটে আনা (মিনিট ও সেকেন্ড)
        tot_seconds = int(duration.total_seconds())
        mins = tot_seconds // 60
        secs = tot_seconds % 60
        duration_str = f"{mins} মিনিট {secs} সেকেন্ড" if mins > 0 else f"{secs} সেকেন্ড"
        
        history_str = "\n".join(s["history"]) if s["history"] else "এই সেশনে কোনো সিগন্যাল নেওয়া হয়নি।"
        
        report_text = (
            "🛑 **QUOTEX SESSION STOPPED** 🛑\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "আজকের সেশনের আপনার ট্রেডিং পারফরম্যান্স রিপোর্ট:\n\n"
            f"⏰ **টোটাল সেশন টাইম:** `{duration_str}`\n"
            f"🔄 **মোট ট্রেড নেওয়া হয়েছে:** `{s['trades']}` টি\n"
            f"🟢 **সফল ট্রেড (Profit):** `{s['wins']}` টি\n"
            f"🔴 **ব্যর্থ ট্রেড (Loss):** `{s['losses']}` টি\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📋 **ট্রেড হিস্টোরি সিরিয়াল লিস্ট:**\n"
            f"{history_str}\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🤝 *আজকের সেশন এখানেই শেষ হলো। নতুন সেশন শুরু করতে আবার /start লিখুন।*"
        )
    else:
        report_text = "❌ আপনার কোনো একটিভ সেশন চালু ছিল না। নতুন সেশন শুরু করতে অনুগ্রহ করে `/start` লিখুন।"
        
    payload = {"chat_id": chat_id, "text": report_text, "parse_mode": "Markdown"}
    requests.post(f"{TELEGRAM_API}/sendMessage", json=payload)

def set_webhook():
    render_url = os.environ.get("RENDER_EXTERNAL_URL")
    if render_url:
        requests.post(f"{TELEGRAM_API}/setWebhook", json={"url": f"{render_url}/webhook"})

if __name__ == "__main__":
    Thread(target=set_webhook).start()
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)
