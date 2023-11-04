import os
from telegram import KeyboardButton, Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
import tensorflow_hub as hub
import tensorflow as tf
import numpy as np
import cv2
from utils.utils import STYLE_TRANSFER, CHOOSE_STYLE, UPLOAD_IMAGE, STYLES
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

model_url = 'https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2'

async def style_transfer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enters the style_transfer mode"""
    user_id = update.message.from_user.id
    db = context.user_data.get('db')
    db.update_user_state(user_id, STYLE_TRANSFER)
    context.user_data['style_transfer'] = NeuralStyleTransfer(model_url)
    print('model successfully fetched')
    await update.message.reply_text(
        "You are now in the style transfer mode. Use /style to start a session, you can upload a file and choose a style. Use /back to return to General mode."
    )

async def style(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asks the user to choose a style from the provided list"""
    user_id = update.message.from_user.id
    db = context.user_data.get('db')
    if db.check_user_state(user_id, STYLE_TRANSFER):
        style_buttons = [[KeyboardButton(style)] for style in STYLES]
        style_markup = ReplyKeyboardMarkup(style_buttons, one_time_keyboard=True, resize_keyboard=True, input_field_placeholder="Please choose a style.")
        await update.message.reply_text("Choose a style:", reply_markup=style_markup)
        return CHOOSE_STYLE
    else:
        await update.message.reply_text("Please start a Style Transfer mode using /style_transfer.")
        return ConversationHandler.END

async def choose_style(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asks the user to uploads an image for style transfer processing"""
    context.user_data['chosen_style'] = update.message.text
    logger.info("user chose: %s", update.message.text)
    await update.message.reply_text("Great! Now, please upload an image.", reply_markup=ReplyKeyboardRemove(),)
    return UPLOAD_IMAGE

async def upload_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processes the image received and sends the result back to the user"""
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    chosen_style = context.user_data['chosen_style']
    transfer_engine = context.user_data['style_transfer']
    await photo_file.download_to_drive("user_photo.jpg")
    processed_image = transfer_engine.pipeline("user_photo.jpg", chosen_style)
    transfer_engine.save_image(processed_image, "temp.jpg")
    chat_id = update.message.chat_id
    await context.bot.send_photo(chat_id, photo=open('temp.jpg', 'rb'))
    os.remove('user_photo.jpg')
    os.remove('temp.jpg')
    logger.info("Photo of %s successfully transfered to %s style", user.first_name, chosen_style)
    await update.message.reply_text("Here is your stylized image. \
                                    You can use /style to try out another style or retun to General mode with /back.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye!", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


class NeuralStyleTransfer:
    style_images = {
        "monet": None,
        "starry_night": None,
        "melody_of_the_night": None,
        "paris_flight": None,
        "riverbank": None,
        "the_scream": None,
        "the_persistence_of_memory": None,
        # Add more style mappings as needed
    }

    def __init__(self, model_url):
        self.model = hub.load(model_url)

    def load_image(self, img_path):
        img = tf.io.read_file(img_path)
        img = tf.image.decode_image(img, channels=3)
        img = tf.image.convert_image_dtype(img, tf.float32)
        img = img[tf.newaxis, :]
        print("Image successfully loaded")
        return img

    def save_image(self, img, filename):
        cv2.imwrite(filename, cv2.cvtColor(np.squeeze(img) * 255, cv2.COLOR_BGR2RGB))

    def stylize_image(self, content_image, style_image):
        stylized_image = self.model(tf.constant(content_image), tf.constant(style_image))[0]
        return stylized_image

    def pipeline(self, content_image_url, style_enum):
        try:
            content_image = self.load_image(content_image_url)
            if style_enum in self.style_images:
                if self.style_images[style_enum] is None:
                    self.style_images[style_enum] = self.load_image('features/style_transfer/style_images/'+style_enum+'.jpg')
                stylized_image = self.stylize_image(content_image, self.style_images[style_enum])
                return stylized_image
            else:
                print(f"Style '{style_enum}' not found. No stylization applied.")
                return content_image
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return None
