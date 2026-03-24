from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)

from rag import get_answer, summarize_text

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

# 🔹 Store user history + last response
user_history = {}
last_response = {}


# ✅ /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello Meghana! 🤖\n\n"
        "Use /ask <question>\n"
        "Use /summarize to summarize last answer\n"
        "Use /help for help"
    )


# ✅ /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/ask <question> - Ask from document\n"
        "/summarize - Summarize last answer\n"
        "/help - Show help"
    )


# ✅ /ask (with history)
async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    query = " ".join(context.args)

    if not query:
        await update.message.reply_text("⚠️ Please provide a question.")
        return

    await update.message.reply_text("Thinking... 🤔")

    # 🔹 Maintain history (last 3)
    if user_id not in user_history:
        user_history[user_id] = []

    user_history[user_id].append(query)
    user_history[user_id] = user_history[user_id][-3:]

    try:
        answer = get_answer(query, user_history[user_id])

        # store last response
        last_response[user_id] = answer

        await update.message.reply_text(answer)

    except Exception as e:
        await update.message.reply_text("❌ Error occurred.")
        print("Error:", e)


# ✅ /summarize
async def summarize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id

    if user_id not in last_response:
        await update.message.reply_text("⚠️ No previous response to summarize.")
        return

    await update.message.reply_text("Summarizing... ✨")

    summary = summarize_text(last_response[user_id])

    await update.message.reply_text(summary)


# 🚀 Main
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ask", ask))
    app.add_handler(CommandHandler("summarize", summarize))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()