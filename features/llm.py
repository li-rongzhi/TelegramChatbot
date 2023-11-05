import os
import openai
from telegram import Update
from telegram.ext import ContextTypes
from utils.utils import LLM



async def llm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enters the LLM mode"""
    user_id = update.message.from_user.id
    db = context.user_data.get('db')
    db.update_user_state(user_id, LLM)
    await update.message.reply_text(
        "You are now in the LLM mode, you can chat freely with ChatGPT. Use /back to return to General mode."
    )
    openai.api_key = os.getenv("OPENAI_API_KEY")

async def get_output(user_input):
    """Get output from the ChatGPT API"""
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": user_input}
        ]
    )
    return completion.choices[0].message['content']