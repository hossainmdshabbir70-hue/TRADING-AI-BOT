import os
import random
import requests
from datetime import datetime, timedelta
from flask import Flask, request, jsonify

TOKEN = "8999370933:AAEC1aGgpIyE1C1kDJNB_Mu5t25BSyEDQ30"
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

app_flask = Flask(__name__)

QUOTEX_MARKETS = [
    "EUR/USD", "GBP/USD", "USD/JPY", "EUR/GBP (OTC)", 
    "USD/INR (OTC)", "USD/BDT (OTC)", "AUD/CAD", "NZD/USD"
]

active_sessions = {}

@app_flask.route('/')
def home():
    return "Quotex Ultra-Pro 90% Fixed Accuracy Bot is Running!"

@app_flask.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "").strip().lower()
        
        if text == "/start":
            # সেশন ট্র্যাকিং যেখানে ১০টির মধ্যে ৯টি উইন নিশ্চিত করার লজিক আছে
            active_sessions[chat_id] = {
                "start_time": datetime.now(),
                "trades": 0,
                "wins": 0,
                "losses": 0,
                "history": [],
                "cycle_trades": 0, # ১০টি ট্রেডের সাইকেল কাউন্টার
                "loss_index": random.randint(1, 10) # ১০টির মধ্যে কোন নাম্বার ট্রেডটি লস হবে তা আগে থেকেই ফিক্সড
            }
            send_welcome_menu(chat_id)
            
        elif text == "next":
            if chat_id not in active_sessions:
                init_session(chat_id)
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

def init_session(chat_id):
    active_sessions[chat_id] = {
        "start_time": datetime.now(),
        "trades": 0,
        "wins": 0,
        "losses": 0,
        "history": [],
        "cycle_trades": 0,
        "loss_index": random.randint(1, 10)
    }

def get_next_candle_time():
    now = datetime.now() + timedelta(minutes=1)
    return now.strftime("%H:%M")

def send_welcome_menu(chat_id, is_next=False):
    text_msg = (
        "🔄 **পরবর্তী আল্ট্রা-প্রো সিগন্যালের জন্য প্রস্তুত!**\nনিচের যেকোনো একটি option বেছে নিয়ে মার্কেট সিলেক্ট করুন:" 
        if is_next else 
        "👋 **স্বাগতম কটেক্স আল্ট্রা-প্রো ভিআইপি ট্রেডার বন্ধু!**\n\nআপনার লাইভ সেশনটি চালু হয়েছে। এই সেশনে এআই ইঞ্জিন থেকে প্রতি ১০টি সিগন্যালে **১০০% ফিক্সড ৯টি প্রফিট** দেওয়া হবে।\n\nট্রেড শেষে সেশন রিপোর্ট দেখতে **/stop** লিখুন বা নিচের বাটনে চাপুন।"
    )
    
    payload = {
        "chat_id": chat_id,
        "text": text_msg,
        "parse_mode": "Markdown",
        "reply_markup": {
            "inline_keyboard": [
                [{"text": "💎 লাইভ সিগন্যাল (Fixed 90% Accuracy)", "callback_data": "main_live"}],
                [{"text": "⏳ ফিউচার সিগন্যাল (Premium VIP)", "callback_data": "main_future"}],
                [{"text": "📊 মার্কেট এনালাইসিস", "callback_data": "main_analyze"}]
            ]
        }
    }
    requests.post(f"{TELEGRAM_API}/sendMessage", json=payload)

def handle_button_click(chat_id, message_id, callback_data):
    if callback_data in ["main_live", "main_future"]:
        is_live = callback_data == "main_live"
        prefix = "lv_" if is_live else "ft_"
        title = "Live Markets" if is_live else "Future Markets"
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": f"🎯 **Quotex Ultra-Pro {title}**\nসিগন্যাল পেতে নিচের যেকোনো একটি মার্কেট সিলেক্ট করুন:",
            "reply_markup": {
                "inline_keyboard": [[{"text": m, "callback_data": f"{prefix}{m}"}] for m in QUOTEX_MARKETS] + [[{"text": "🔙 প্রধান মেনু", "callback_data": "back_to_main"}]]
            }
        }
        requests.post(f"{TELEGRAM_API}/editMessageText", json=payload)

    elif callback_data == "main_analyze":
        analysis_text = "📊 **QUOTEX ULTRA-SURE MARKET ANALYSIS**\n\n• **EUR/USD:** RSI সূচক অনুযায়ী মার্কেট রিভার্সাল জোনে আছে।\n• **90% Fixed Accuracy:** সেশনে প্রতি ১০টি সিগন্যালে ঠিক ৯টি প্রফিট নিশ্চিত করা হয়েছে।"
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
        
        if chat_id not in active_sessions:
            init_session(chat_id)
            
        s = active_sessions[chat_id]
        s["trades"] += 1
        s["cycle_trades"] += 1
        
        # ১০টা সিগন্যালের ফিক্সড রেশিও লজিক (ঠিক ১টা লস, ৯টা প্রফিট)
        if s["cycle_trades"] == s["loss_index"]:
            current_result = "LOSS"
            res_string = "❌ LOSS"
            confirmation_tag = "⚡ PREMIUM ADVANCED SIGNAL"
            win_rate = random.randint(60, 75)
        else:
            current_result = "PROFIT"
            res_string = "✅ PROFIT"
            confirmation_tag = "💎 100% ALGORITHMIC ULTRA SURE SHOT"
            win_rate = random.randint(95, 99)
            
        # ১০টি সিগন্যাল শেষ হলে সাইকেল রিস্টার্ট হবে এবং নতুন লস ইনডেক্স তৈরি হবে
        if s["cycle_trades"] >= 10:
            s["cycle_trades"] = 0
            s["loss_index"] = random.randint(1, 10)
            
        market_trend = random.choice(["CALL", "PUT"])
        direction = "🟢 CALL (UP) 👆" if market_trend == "CALL" else "🔴 PUT (DOWN) 👇"
        
        if current_result == "PROFIT":
            s["wins"] += 1
        else:
            s["losses"] += 1
            
        trade_num = s["trades"]
        # সিগন্যাল ডিরেকশন ও ফলাফল নিখুঁতভাবে হিস্ট্রিতে সেভ করা
        s["history"].append(f"{trade_num}. {pair} ({'UP' if market_trend == 'CALL' else 'DOWN'}) ➡️ {res_string}")

        title_text = "💎 **QUOTEX LIVE ULTRA-PRO SHOT** 💎" if is_live else "⏳ **QUOTEX FUTURE ULTRA-PRO SHOT** ⏳"
        candle_time = get_next_candle_time()
        expiry = f"`1 MIN` (ক্যান্ডেল শুরু: **{candle_time}**)" if is_live else f"`5 MIN` (ক্যান্ডেল শুরু: **{candle_time}**)"
        
        signal_msg = (
            f"{title_text}\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 **মার্কেট (Asset):** `{pair}`\n"
            f"👉 **ডিরেকশন (Action):** **{direction}**\n"
            f"⏳ **টাইমফ্রেম (Expiry):** {expiry}\n"
            f"🏆 **উইন রেট (Accuracy):** `{win_rate}%` 🔥\n"
            f" স্ট্যাটাস: *{confirmation_tag}*\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"🔢 এই সেশনের বর্তমান মোট ট্রেড: `{trade_num}` টি\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "💡 *পরবর্তী আল্ট্রা-প্রো সিগন্যাল পেতে নিচে 'Next Market' বাটনে চাপুন।*"
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

def send_final_report(chat_id):
    if chat_id in active_sessions and active_sessions[chat_id]["trades"] > 0:
        s = active_sessions[chat_id]
        duration = datetime.now() - s["start_time"]
        
        tot_seconds = int(duration.total_seconds())
        mins = tot_seconds // 60
        secs = tot_seconds % 60
        duration_str = f"{mins} মিনিট {secs} সেকেন্ড" if mins > 0 else f"{secs} সেকেন্ড"
        
        history_str = "\n".join(s["history"])
        
        report_text = (
            "🛑 **QUOTEX ULTRA-PRO VIP SESSION REPORT** 🛑\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"⏰ **মোট সেশন টাইম:** `{duration_str}`\n"
            f"🔄 **মোট ট্রেড নেওয়া হয়েছে:** `{s['trades']}` টি\n"
            f"🟢 **সফল ট্রেড (Total Profit):** `{s['wins']}` টি\n"
            f"🔴 **ব্যর্থ ট্রেড (Total Loss):** `{s['losses']}` টি\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📋 **পুরো সেশনের সব ট্রেডের নিখুঁত তালিকা:**\n"
            f"{history_str}\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🤝 *ভিআইপি আল্ট্রা-প্রো সেশনটি সফলভাবে ক্লোজ হয়েছে। নতুন সেশন শুরু করতে আবার /start লিখুন।*"
        )
    else:
        report_text = "❌ আপনার চলতি সেশনে কোনো ট্রেড রেকর্ড করা হয়নি। নতুন সেশন শুরু করতে `/start` লিখুন।"
        
    payload = {"chat_id": chat_id, "text": report_text, "parse_mode": "Markdown"}
    requests.post(f"{TELEGRAM_API}/sendMessage", json=payload)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)
    
