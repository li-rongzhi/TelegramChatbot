from telegram import Update
from telegram.ext import ContextTypes
from utils.utils import GENERAL, TIMER

async def timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enters the timer mode"""
    user_id = update.message.from_user.id
    db = context.user_data.get('db')
    if db.check_user_state(user_id, TIMER):
        await update.message.reply_text("You are already in the Timer mode")
    else:
        db.update_user_state(user_id, TIMER)
        await update.message.reply_text(
            "You are now in the Timer mode. Use /set to set timer or /unset to unset existing timer."
        )


async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the alarm message"""
    job = context.job
    await context.bot.send_message(job.chat_id, text=f"Beep! {job.data} seconds are over!")


def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Removes job with given name. Returns whether job was removed"""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True

async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sets a new timer"""
    chat_id = update.effective_message.chat_id
    user_id = update.message.from_user.id
    db = context.user_data.get('db')
    if not db.check_user_state(user_id, TIMER):
        await update.message.reply_text("Please enter Timer mode using /timer.")
        return
    try:
        # args[0] should contain the time for the timer in seconds
        due = float(context.args[0])
        if due < 0:
            await update.effective_message.reply_text("Sorry we can not go back to future!")
            return

        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_once(alarm, due, chat_id=chat_id, name=str(chat_id), data=due)

        text = "Timer successfully set!"
        if job_removed:
            text += " Old one was removed."
        await update.effective_message.reply_text(text)

    except (IndexError, ValueError):
        await update.effective_message.reply_text("Usage: /set <seconds>")


async def unset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Cancels the lastly added timer"""
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    db = context.user_data.get('db')
    if not db.check_user_state(user_id, TIMER):
        await update.message.reply_text("Please enter Timer mode using /timer.")
        return
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = "Timer successfully cancelled!" if job_removed else "You have no active timer."
    await update.message.reply_text(text)

