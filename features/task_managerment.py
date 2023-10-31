import re
from telegram import Update
from telegram.ext import ContextTypes
from utils.utils import GENERAL, TASK_MANAGEMENT


async def task_management(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    db = context.user_data.get('db')
    db.update_user_state(user_id, TASK_MANAGEMENT)
    await update.message.reply_text(
        "You are now in the Task Management session. Use /add to add tasks or /list to list your tasks."
    )

async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    db = context.user_data.get('db')
    if db.check_user_state(user_id, TASK_MANAGEMENT):
        user_input = ' '.join(context.args)
        print(user_input)
        pattern = r'([dts])/(.*?)\s*(?=[dts]/|\Z)'
        fields = re.findall(pattern, user_input)
        print(fields)
        task_data = {'user_id': user_id, 'description':'', 'duetime': '', 'remark': ''}
        for prefix, value in fields:
            if prefix == 'd':
                task_data['description'] = value
            elif prefix == 't':
                task_data['duetime'] = value
            elif prefix == 'r':
                task_data['remark'] = value
        print(task_data)
        db.add_task(**task_data)
        await update.message.reply_text("Task added successfully!")
    else:
        await update.message.reply_text("Please start a Task Management session using /task.")

async def delete_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    db = context.user_data.get('db')
    if db.check_user_state(user_id, TASK_MANAGEMENT):
        db.delete_task(user_id, context.args[0])
        await update.message.reply_text("Task deleted successfully!")
    else:
        await update.message.reply_text("Please start a Task Management session using /task.")

async def mark_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    db = context.user_data.get('db')
    if db.check_user_state(user_id, TASK_MANAGEMENT):
        task_id = context.args[0]
        db.mark_task(user_id, task_id)
    else:
        await update.message.reply_text("Please start a Task Management session using /task.")

async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    db = context.user_data.get('db')
    if db.check_user_state(user_id, TASK_MANAGEMENT):
        tasks = db.list_tasks(user_id)
        if tasks:
            headers = ["Task ID", "Description", "Is Done", "Remark", "Due"]
            header_string = " | ".join(headers)
            task_rows = [header_string]
            for task in tasks:
                task_str = " | ".join(str(column) for column in task)
                task_rows.append(task_str)
            task_list = "\n".join(task_rows)
            await update.message.reply_text(f"Your tasks:\n{task_list}")
        else:
            await update.message.reply_text("You have no tasks.")
    else:
        await update.message.reply_text("Please start a Task Management session using /task.")

