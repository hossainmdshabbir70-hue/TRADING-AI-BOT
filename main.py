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
