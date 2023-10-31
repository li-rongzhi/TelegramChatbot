from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import os
from database.db import MySQLDatabase
from features.llm import llm, get_output
from features.task_managerment import add_task, delete_task, list_tasks, mark_task, task_management
from features.timer import set_timer, unset

from utils.utils import GENERAL, LLM, TASK_MANAGEMENT, TIMER


db_password = os.environ.get('DB_PASSWORD')
configs = {
    'host':'localhost',
    'user': 'root',
    'password':db_password,
    'database':'telebot'
}


# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
async def start(update: Update, context: MySQLDatabase):
    context.user_data['db'] = MySQLDatabase(**configs)
    user_id = update.message.from_user.id
    db = context.user_data.get('db')
    db.connect()
    db.initialize()
    db.initialize_user_state(str(user_id))
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Help!")

async def back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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

    application.add_handler(CommandHandler("llm", llm))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
