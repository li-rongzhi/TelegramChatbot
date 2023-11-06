from telegram import Update, ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler
import os
from database.db import MySQLDatabase
from features.llm import llm, get_output
from features.news import get_news, select_category
from features.task_managerment import add_task, delete_task, list_tasks, mark_task, task_management
from features.timer import set_timer, unset
from features.style_transfer.style_transfer import style_transfer, style, choose_style, upload_image, cancel
import features.style_transfer.style_transfer as st
import features.news as news
from utils.utils import GENERAL, LLM, CHOOSE_STYLE, UPLOAD_IMAGE, STYLES, GET_NEWS, NEWS_CATEGORY

intro_message = """
Welcome to Jarvis! Here are some of my functionalities:

1. <b>/task</b>
    - Handle your todo list.
2. <b>/llm</b>
    - Chat freely with ChatGPT.
3. <b>/style_transfer</b>
    - Transfer your image to predefined styles.
4. <b>/news</b>
    - Stay updated with the latest news.
5. <b>/help</b>
    - Access the user guide for more information.
You can use these shortcuts to access each functionality.
"""

# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
async def start(update: Update, context: MySQLDatabase):
    db_password = os.getenv('DB_PASSWORD')
    configs = {
        'host':'localhost',
        'user': 'root',
        'password':db_password,
        'database':'telebot'
    }
    context.user_data['db'] = MySQLDatabase(**configs)
    user_id = update.message.from_user.id
    db = context.user_data.get('db')
    db.connect()
    db.initialize()
    db.initialize_user_state(str(user_id))
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!{intro_message}"
    )

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = "You can check out the [user guide](https://li-rongzhi.github.io/TelegramChatbot/user_guide.html) in Markdown format."
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

async def back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    db = context.user_data.get('db')
    db.update_user_state(user_id, GENERAL)
    await update.message.reply_text("You are back to GENERAL mode now.")

async def exit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Bye!")

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    db = context.user_data.get('db')
    if db.check_user_state(user_id, LLM):
        output = await get_output(update.message.text)
        await update.message.reply_text(output)
    else:
        await update.message.reply_text(update.message.text)

def setup(application: Application):
    # basic setup
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("exit", exit))
    application.add_handler(CommandHandler("back", back))

    # timer functionality
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
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
