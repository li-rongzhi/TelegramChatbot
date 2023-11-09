import asyncio
import os
import openai
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from utils.utils import LLM
from app import db
import tiktoken

async def llm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enters the LLM mode"""
    user_id = update.message.from_user.id
    db.update_user_state(user_id, LLM)
    db.start_new_dialog(user_id)
    await update.message.reply_text(
        "You are now in the LLM mode, you can chat freely with ChatGPT. Use /back to return to General mode."
    )
    openai.api_key = os.getenv("OPENAI_API_KEY")

async def start_new_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    db.start_new_dialog(user_id)
    await update.message.reply_text(
        "You have started a new dialog session."
    )

async def send_request(user_input, dialog_history):
    answer = None
    n_dialog_messages_before = len(dialog_history)
    while answer is None:
        try:
            prompt = str(generate_prompt(user_input, dialog_history))
            r_gen = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant"},
                    {"role": "user", "content": prompt}
                ],
                stream=True
            )
            answer = ""
            async for r_item in r_gen:
                delta = r_item.choices[0].delta
                if "content" in delta:
                    answer += delta.content
                    n_input_tokens, n_output_tokens = count_tokens_from_prompt(prompt, answer)
                    n_first_dialog_messages_removed = n_dialog_messages_before - len(dialog_history)
                    yield "not_finished", answer, (n_input_tokens, n_output_tokens), n_first_dialog_messages_removed
        except openai.error.InvalidRequestError as e:  # too many tokens
                if len(dialog_history) == 0:
                    raise ValueError("Dialog messages is reduced to zero, but still has too many tokens to make completion") from e
                    # forget first message in dialog_messages
                dialog_history = dialog_history[1:]
    yield "finished", answer, (n_input_tokens, n_output_tokens), n_first_dialog_messages_removed

async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE, user_input: str):
    user_id = update.message.from_user.id
    if not db.check_tokens(user_id, 1000) and not db.get_user_attribute(user_id, "isPremium"):
        await update.message.reply_text("Sorry, you have reached the maximum usage. Please /upgrade for unlimited access.")
        return
    placeholder_message = await update.message.reply_text("...")
    await update.message.chat.send_action(action="typing")
    prev_answer = ""
    dialog_history = db.get_dialog_messages(user_id, dialog_id=None)
    gen = send_request(user_input, dialog_history=dialog_history)
    async for gen_item in gen:
        status, answer, (n_input_tokens, n_output_tokens), n_first_dialog_messages_removed = gen_item
        answer = answer[:4096]
        if abs(len(answer) - len(prev_answer)) < 50 and status != "finished":
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
    db.update_n_used_tokens(user_id, n_input_tokens, n_output_tokens)
    if n_first_dialog_messages_removed > 0:
        if n_first_dialog_messages_removed == 1:
            text = "✍️ <i>Note:</i> Your current dialog is too long, so your <b>first message</b> was removed from the context.\n Send /new command to start new dialog"
        else:
            text = f"✍️ <i>Note:</i> Your current dialog is too long, so <b>{n_first_dialog_messages_removed} first messages</b> were removed from the context.\n Send /new command to start new dialog"
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)


def generate_prompt(user_input, dialog_history):
    messages = []
    for dialog_message in dialog_history:
        messages.append({"role": "user", "content": dialog_message["user"]})
        messages.append({"role": "assistant", "content": dialog_message["bot"]})
    messages.append({"role": "user", "content": user_input})
    return messages

def count_tokens_from_messages(messages, answer, model="gpt-3.5-turbo"):
    encoding = tiktoken.encoding_for_model(model)
    tokens_per_message = 4
    n_input_tokens = 0
    for message in messages:
        n_input_tokens += tokens_per_message
        for key, value in message.items():
            n_input_tokens += len(encoding.encode(value))
    n_input_tokens += 2
    n_output_tokens = 1 + len(encoding.encode(answer))

    return n_input_tokens, n_output_tokens

def count_tokens_from_prompt(prompt, answer, model="gpt-3.5-turbo"):
        encoding = tiktoken.encoding_for_model(model)
        n_input_tokens = len(encoding.encode(prompt)) + 1
        n_output_tokens = len(encoding.encode(answer))
        return n_input_tokens, n_output_tokens