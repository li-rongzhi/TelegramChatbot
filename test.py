import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, Updater, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
import os

# Enable logging (optional)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
# Define conversation states
CHOOSE_STYLE, UPLOAD_IMAGE, SEND_OUTPUT = range(3)

# Define a dictionary to store user's style choice
user_data = {}

# Define the start function
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to the Style Transfer Bot! Send /style to choose a style.")

async def style(update: Update, context: ContextTypes.DEFAULT_TYPE):
    style_keyboard = [['Style 1', 'Style 2', 'Style 3', 'Style 4']]

    # Convert the list of buttons into a keyboard
    style_markup = ReplyKeyboardMarkup(style_keyboard, one_time_keyboard=True, input_field_placeholder="Please choose a style.")

    # Send a message with the style choices
    await update.message.reply_text("Choose a style:", reply_markup=style_markup)
    return CHOOSE_STYLE

# Define the function to ask the user to choose a style
async def choose_style(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    context.user_data['chosen_style'] = update.message.text
    logger.info("user chose: %s", update.message.text)
    await update.message.reply_text("Great! Now, please upload an image.", reply_markup=ReplyKeyboardRemove(),)
    return UPLOAD_IMAGE

async def upload_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    chosen_style = context.user_data['chosen_style']
    await photo_file.download_to_drive("user_photo.jpg")
    logger.info("Photo of %s: %s transfered to %s", user.first_name, "user_photo.jpg", chosen_style)
    await update.message.reply_text(
        "Gorgeous!"
    )
    await update.message.reply_text("Here is your stylized image. You can use /style to choose another style.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def main():
    chatbot_token = os.environ.get('CHATBOT_TOKEN')
    # Initialize the Updater with your bot's token
    application = Application.builder().token(chatbot_token).build()


    # Define the conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('style', style)],
        states={
            CHOOSE_STYLE: [MessageHandler(filters.Regex("^(Style) [1-4]$"), choose_style)],
            UPLOAD_IMAGE: [MessageHandler(filters.PHOTO, upload_image)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
