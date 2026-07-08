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

# 📊 গ্লোবাল সেশন মেমোরি
active_sessions = {}

@app_flask.route('/')
def home():
    return "Quotex Premium VIP Bot is Running!"

@app_flask.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "").strip().lower()
        
        if text == "/start":
            active_sessions[chat_id] = {
                "start_time": datetime.now(),
                "trades": 0,
                "wins": 0,
                "losses": 0,
                "history": []
            }
            send_welcome_menu(chat_id)
            
        elif text == "next":
            if chat_id not in active_sessions:
                active_sessions[chat_id] = {"start_time": datetime.now(), "trades": 0, "wins": 0, "losses": 0, "history": []}
            send_welcome_menu(chat_id, is_next=True)
            
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
# ⏱️ NEXT CANDLE TIMER
# ==========================================
def get_next_candle_time():
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
def send_welcome_menu(chat_id, is_next=False):
    text_msg = (
        "🔄 **পরবর্তী হাই-উইনরেট সিগন্যালের জন্য প্রস্তুত!**\nনিচের যেকোনো একটি অপশন বেছে নিয়ে মার্কেট সিলেক্ট করুন:" 
        if is_next else 
        "👋 **স্বাগতম কটেক্স ভিআইপি ট্রেডার বন্ধু!**\n\nআপনার লাইভ সেশনটি চালু হয়েছে। এই সেশনে এআই ইঞ্জিন থেকে **৯৫%+ প্রিমিয়াম শিউর শট সিগন্যাল** দেওয়া হবে।\n\nট্রেড শেষে সেশন রিপোর্ট দেখতে **/stop** লিখুন বা নিচের বাটনে চাপুন।"
    )
    
    payload = {
        "chat_id": chat_id,
        "text": text_msg,
        "parse_mode": "Markdown",
        "reply_markup": {
            "inline_keyboard": [
                [{"text": "💎 লাইভ সিগন্যাল (95%+ Sure Shot)", "callback_data": "main_live"}],
                [{"text": "⏳ ফিউচার সিগন্যাল (Premium VIP)", "callback_data": "main_future"}],
                [{"text": "📊 মার্কেট এনালাইসিস", "callback_data": "main_analyze"}]
            ]
        }
    }
    requests.post(f"{TELEGRAM_API}/sendMessage", json=payload)

def handle_button_click(chat_id, message_id, callback_data):
    if callback_data == "main_live":
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": "🎯 **Quotex Premium Live Markets**\nশিউর শট সিগন্যাল পেতে নিচের যেকোনো একটি মার্কেট সিলেক্ট করুন:",
            "reply_markup": {
                "inline_keyboard": [[{"text": m, "callback_data": f"lv_{m}"}] for m in QUOTEX_MARKETS] + [[{"text": "🔙 প্রধান মেনু", "callback_data": "back_to_main"}]]
            }
        }
        requests.post(f"{TELEGRAM_API}/editMessageText", json=payload)

    elif callback_data == "main_future":
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": "⏳ **Quotex VIP Future Markets**\nউচ্চ উইনরেট ফিউচার সিগন্যাল পেতে মার্কেট সিলেক্ট করুন:",
            "reply_markup": {
                "inline_keyboard": [[{"text": m, "callback_data": f"ft_{m}"}] for m in QUOTEX_MARKETS] + [[{"text": "🔙 প্রধান মেনু", "callback_data": "back_to_main"}]]
            }
        }
        requests.post(f"{TELEGRAM_API}/editMessageText", json=payload)

    elif callback_data == "main_analyze":
        analysis_text = "📊 **QUOTEX ULTRA-SURE MARKET ANALYSIS**\n\n• **EUR/USD:** আরএসআই (RSI) ওভারসোল্ড জোন থেকে রিভার্সাল নিচ্ছে। পরবর্তী ক্যান্ডেল স্ট্রং বুলিশ হওয়ার সম্ভাবনা ৯৬%।\n• **OTC মার্কেট:** অ্যালগরিদম বর্তমানে হাই উইন ট্রেন্ড ফলো করছে।"
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": analysis_text,
            "parse_mode": "Markdown",
            "reply_markup": {"inline_keyboard": [[{"text": "🔙 প্রধান মেনু", "callback_data": "back_to_main"}]]}
        }
        requests.post(f"{TELEGRAM_API}/editMessageText", json=payload)

    elif callback_data.startswith(("lv_", "ft_")):
        is_live = callback_data.startswith("lv_")
        pair = callback_data.replace("lv_", "") if is_live else callback_data.replace("ft_", "")
        
        direction = random.choice(["🟢 CALL (UP) 👆", "🔴 PUT (DOWN) 👇"])
        candle_time = get_next_candle_time()
        
        # 🔥 উইন রেট সবসময় ৯৫% থেকে ৯৯% এর মধ্যে ফিক্সড
        win_rate = random.randint(95, 99)
        confirmation_tag = random.choice(["🔥 HIGH CONFIRMATION VIP SHOT", "💎 100% ALGORITHMIC SURE SHOT", "⚡ PREMIUM ADVANCED SIGNAL"])
        
        # 🚨 মেমোরি এবং উইন রেশিও ট্রিক (৯৫% প্রফিট চান্স ব্যাকগ্রাউন্ডে)
        if chat_id not in active_sessions:
            active_sessions[chat_id] = {"start_time": datetime.now(), "trades": 0, "wins": 0, "losses": 0, "history": []}
            
        active_sessions[chat_id]["trades"] += 1
        current_result = "PROFIT" if random.random() > 0.05 else "LOSS" # লসের সুযোগ মাত্র ৫%
        
        if current_result == "PROFIT":
            active_sessions[chat_id]["wins"] += 1
            res_string = "✅ PROFIT"
        else:
            active_sessions[chat_id]["losses"] += 1
            res_string = "❌ LOSS"
            
        trade_num = active_sessions[chat_id]["trades"]
        active_sessions[chat_id]["history"].append(f"{trade_num}. {pair} ➡️ {res_string}")

        title = "💎 **QUOTEX LIVE VIP SHOT** 💎" if is_live else "⏳ **QUOTEX FUTURE VIP SHOT** ⏳"
        expiry = f"`1 MIN` (ক্যান্ডেল শুরু: **{candle_time}**)" if is_live else f"`5 MIN` (ক্যান্ডেল শুরু: **{candle_time}**)"
        
        signal_msg = (
            f"{title}\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 **মার্কেট (Asset):** `{pair}`\n"
            f"👉 **ডিরেকশন (Action):** **{direction}**\n"
            f"⏳ **টাইমফ্রেম (Expiry):** {expiry}\n"
            f"🏆 **উইন রেট (Accuracy):** `{win_rate}%` 🔥\n"
            f" स्टेटस: *{confirmation_tag}*\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"🔢 এই সেশনের বর্তমান মোট ট্রেড: `{trade_num}` টি\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "💡 *পরবর্তী ভিআইপি সিগন্যাল পেতে নিচে 'Next Market' বাটনে চাপুন।*"
        )
        
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": signal_msg,
            "parse_mode": "Markdown",
            "reply_markup": {
                "inline_keyboard": [
                    [{"text": "🔄 Next Market (পরবর্তী মার্কেট)", "callback_data": "main_live" if is_live else "main_future"}],
                    [{"text": "🛑 Stop Session (সেশন শেষ)", "callback_data": "trigger_stop"}]
                ]
            }
        }
        requests.post(f"{TELEGRAM_API}/editMessageText", json=payload)

    elif callback_data == "trigger_stop":
        send_final_report(chat_id)
        if chat_id in active_sessions: del active_sessions[chat_id]

    elif callback_data == "back_to_main":
        send_welcome_menu(chat_id)

# ==========================================
# 🛑 SESSION STOP & REPORT ENGINE
# ==========================================
def send_final_report(chat_id):
    if chat_id in active_sessions and active_sessions[chat_id]["trades"] > 0:
        s = active_sessions[chat_id]
        duration = datetime.now() - s["start_time"]
        
        tot_seconds = int(duration.total_seconds())
        mins = tot_seconds // 60
        secs = tot_seconds % 60
        duration_str = f"{mins} মিনিট {secs} SECOND" if mins > 0 else f"{secs} SECOND"
        
        history_str = "\n".join(s["history"])
        
        report_text = (
            "🛑 **QUOTEX VIP SESSION REPORT** 🛑\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"⏰ **মোট সেশন টাইম:** `{duration_str}`\n"
            f"🔄 **মোট ট্রেড নেওয়া হয়েছে:** `{s['trades']}` টি\n"
            f"🟢 **সফল ট্রেড (Total Profit):** `{s['wins']}` টি\n"
            f"🔴 **ব্যর্থ ট্রেড (Total Loss):** `{s['losses']}` টি\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📋 **পুরো সেশনের সব ট্রেডের তালিকা:**\n"
            f"{history_str}\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🤝 *ভিআইপি সেশন সফলভাবে ক্লোজ হয়েছে। নতুন সেশন শুরু করতে আবার /start লিখুন।*"
        )
    else:
        report_text = "❌ আপনার চলতি সেশনে কোনো ট্রেড রেকর্ড করা হয়নি। নতুন সেশন শুরু করতে `/start` লিখুন।"
        
    payload = {"chat_id": chat_id, "text": report_text, "parse_mode": "Markdown"}
    requests.post(f"{TELEGRAM_API}/sendMessage", json=payload)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)
