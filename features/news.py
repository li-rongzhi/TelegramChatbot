import os
import requests
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, ConversationHandler
from app import db
from utils.utils import NEWS, NEWS_CATEGORY, GET_NEWS, ENDPOINT
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enters the news mode"""
    user_id = update.message.from_user.id
    if db.check_user_state(user_id, NEWS):
        await update.message.reply_text("You are already in the News mode")
    else:
        db.update_user_state(user_id, NEWS)
        logger.info("User %s enters News mode", user_id)
        await update.message.reply_text(
            "You are now in the News mode. " + \
            "Stay updated with the latest news. Use /get_news to fetch trending news online. \U0001F680"
        )

async def select_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asks user to select a interested category"""
    user_id = update.message.from_user.id
    if db.check_user_state(user_id, NEWS):
        style_buttons = [[KeyboardButton(category)] for category in NEWS_CATEGORY]
        style_markup = ReplyKeyboardMarkup(style_buttons, one_time_keyboard=True, resize_keyboard=True, input_field_placeholder="Please choose a style.")
        await update.message.reply_text("Select a category:", reply_markup=style_markup)
        return GET_NEWS
    else:
        await update.message.reply_text("Please start a Style Transfer mode using /style_transfer.")
        return ConversationHandler.END

async def get_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gets popular news through NEWS API"""
    context.user_data['category'] = update.message.text
    logger.info("user chose: %s", update.message.text)
    await update.message.reply_text('Great! Please wait a moment.', reply_markup=ReplyKeyboardRemove())
    params = {
        'apiKey': os.getenv("NEWS_API_KEY"),
        'category': update.message.text,
        'country': 'us'
    }
    try:
        # Make the API request
        response = requests.get(ENDPOINT, params=params)
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            data = response.json()
            # Check if there are articles in the response
            if 'articles' in data:
                articles = data['articles']
                news_message = "<b>Here are the latest news articles:</b>\n\n"
                await update.message.reply_html(news_message)
                # Display the top headlines
                for article in articles[:3]:
                    title = article.get('title', 'N/A')
                    url = article.get('url')
                    news_message = f"<a href='{url}'><b>{title}</b></a> \n"
                    description = article.get('description')
                    if description:
                        news_message += f"<i>{description}</i>\n\n"
                    else:
                        news_message += "\n"
                    await update.message.reply_html(news_message)
            else:
                await update.message.reply_text("No articles found in the response.")
        else:
            await update.message.reply_text("No articles found in the response.")
        return ConversationHandler.END
    except Exception as e:
        print("An error occurred:", e)
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation in News.", user.first_name)
    await update.message.reply_text(
        "Bye!", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END