from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler, CallbackContext
import os
from app import CustomContext
from database.db import MySQLDatabase
from database.mongo_db import MongoDB
from features.llm import llm, send_message, start_new_dialog
from features.news import get_news, select_category
from features.task_managerment import add_task, delete_task, list_tasks, mark_task, task_management
from features.timer import set_timer, unset, timer
from features.style_transfer.style_transfer import style_transfer, style, choose_style, upload_image, cancel
import features.style_transfer.style_transfer as st
import features.news as news
from utils.utils import GENERAL, LLM, CHOOSE_STYLE, UPLOAD_IMAGE, STYLES, GET_NEWS, NEWS_CATEGORY
from app import db
intro_message = """
Welcome to Jarvis! Here are some of my functionalities:

1. <b>/task</b>
    - Handle your todo list.
2. <b>/llm</b>
    - Chat freely with <i>ChatGPT</i>.
3. <b>/style_transfer</b>
    - Transfer your image to predefined styles.
4. <b>/news</b>
    - Stay updated with the latest news.
5. <b>/timer</b>
    - Set a timer for productivity.
6. <b>/upgrade</b>
    - Upgrade to <i>Premium</i> for unlimited LLM access (no payment needed for now).
7. <b>/help</b>
    - Access the User Guide for more information.

You can use these shortcuts to access each functionality.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    db.add_user(user_id=user_id)
    db.initialize_user_state(user_id)
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!{intro_message}"
    )

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = "You can check out the [User Guide](https://li-rongzhi.github.io/TelegramChatbot/user_guide.html)."
    await update.message.reply_text(message, parse_mode="Markdown")

async def back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    db.update_user_state(user_id, GENERAL)
    await update.message.reply_text("You are back to GENERAL mode now.")

async def exit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Bye!")

async def upgrade(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    db.upgrade_user(user_id)
    await update.message.reply_text("You have successfully upgraded to Premium.")

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if db.check_user_state(user_id, LLM):
        await send_message(update=update, context=context, user_input=update.message.text)
    else:
        await update.message.reply_text(update.message.text)

def setup(application: Application):
    # basic setup
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("exit", exit))
    application.add_handler(CommandHandler("back", back))
    application.add_handler(CommandHandler("upgrade", upgrade))

    # timer functionality
    application.add_handler(CommandHandler("timer", timer))
    application.add_handler(CommandHandler("set", set_timer))
    application.add_handler(CommandHandler("unset", unset))

    # task management functionality
    application.add_handler(CommandHandler("task", task_management))
    application.add_handler(CommandHandler("add", add_task))
    application.add_handler(CommandHandler("list", list_tasks))
    application.add_handler(CommandHandler("delete", delete_task))
    application.add_handler(CommandHandler("mark", mark_task))

    # style transfer functionality
    application.add_handler(CommandHandler("style_transfer", style_transfer))
    style_transfer_handler = ConversationHandler(
        entry_points=[CommandHandler('style', style)],
        states={
            CHOOSE_STYLE: [MessageHandler(filters.Text(STYLES), choose_style)],
            UPLOAD_IMAGE: [MessageHandler(filters.PHOTO, upload_image)],
        },
        fallbacks=[CommandHandler("cancel", st.cancel)]
    )
    application.add_handler(style_transfer_handler)

    # news catcher functionality
    application.add_handler(CommandHandler("news", news.news))
    news_handler = ConversationHandler(
        entry_points=[CommandHandler('get_news', select_category)],
        states={
            GET_NEWS: [MessageHandler(filters.Text(NEWS_CATEGORY), get_news)],
        },
        fallbacks=[CommandHandler("cancel", news.cancel)]
    )
    application.add_handler(news_handler)

    # llm functionality
    application.add_handler(CommandHandler("llm", llm))
    application.add_handler(CommandHandler("new", start_new_dialog))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
