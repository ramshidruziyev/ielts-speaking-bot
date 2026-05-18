import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
from groq import Groq

logging.basicConfig(level=logging.INFO)

groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

user_sessions = {}

SYSTEM_PROMPT = """You are an IELTS Speaking examiner and coach. Your job is to:
1. Ask IELTS Speaking questions (Part 1, 2, or 3)
2. Listen to the user's answer
3. Give feedback on: Fluency, Vocabulary, Grammar, Pronunciation tips
4. Give an estimated Band Score (1-9)
5. Encourage and help them improve

Start by asking a Part 1 question about a familiar topic like hometown, work, or hobbies.
Always be encouraging and professional."""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_sessions[user_id] = []
    await update.message.reply_text(
        "👋 Welcome to IELTS Speaking Practice Bot!\n\n"
        "I'm your AI examiner. I'll ask you questions and give feedback.\n\n"
        "Type anything to start! 🎯"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text

    if user_id not in user_sessions:
        user_sessions[user_id] = []

    user_sessions[user_id].append({"role": "user", "content": user_text})

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + user_sessions[user_id][-10:]

    response = groq_client.chat.completions.create(
        model="llama3-70b-8192",
        messages=messages,
        max_tokens=500,
    )

    reply = response.choices[0].message.content
    user_sessions[user_id].append({"role": "assistant", "content": reply})

    await update.message.reply_text(reply)

def main():
    token = os.environ.get("BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
