import asyncio
import os
import openai
from telegram import Update
from telegram.ext import ContextTypes
from utils.utils import LLM
from app import db


async def llm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enters the LLM mode"""
    user_id = update.message.from_user.id
    db.update_user_state(user_id, LLM)
    db.start_new_dialog(user_id)
    await update.message.reply_text(
        "You are now in the LLM mode, you can chat freely with ChatGPT. Use /back to return to General mode."
    )
    openai.api_key = os.getenv("OPENAI_API_KEY")

async def send_request(user_input, dialog_history):
    prompt = generate_prompt(user_input, dialog_history)
    print(prompt)
    r_gen = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": str(prompt)}
        ],
        stream=True
    )
    print(dialog_history)
    answer = ""
    async for r_item in r_gen:
        delta = r_item.choices[0].delta
        if "content" in delta:
            answer += delta.content
            yield "not_finished", answer
    yield "finished", answer

async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE, user_input: str):
    await update.message.chat.send_action(action="typing")
    placeholder_message = await update.message.reply_text("...")
    prev_answer = ""
    user_id = update.message.from_user.id
    dialog_history = db.get_dialog_messages(user_id, dialog_id=None)
    print(dialog_history)
    gen = send_request(user_input, dialog_history=dialog_history)
    async for gen_item in gen:
        status, answer = gen_item

        answer = answer[:4096]

        if abs(len(answer) - len(prev_answer)) < 100 and status != "finished":
            continue
        await context.bot.edit_message_text(answer, chat_id=placeholder_message.chat_id, message_id=placeholder_message.message_id)
        await asyncio.sleep(0.01)
        prev_answer = answer
    new_dialog_message = {"user": user_input, "bot": answer}
    db.set_dialog_messages(
        user_id,
        db.get_dialog_messages(user_id, dialog_id=None) + [new_dialog_message],
        dialog_id=None
    )

def generate_prompt(user_input, dialog_history):
    messages = []
    for dialog_message in dialog_history:
        messages.append({"role": "user", "content": dialog_message["user"]})
        messages.append({"role": "assistant", "content": dialog_message["bot"]})
    messages.append({"role": "user", "content": user_input})
    return messages