# Deployment Instructions

Follow these steps to deploy the Telegram Chatbot in your environment:

## Prerequisites

- Have a Telegram account.
- Have MySQL database installed.
- Access to the Telegram Bot API to create a bot.
- Knowledge of your bot's API token.

## BOT Setup

1. **Clone the Repository:**
    - Clone this repository to your local machine using Git or download it as a ZIP archive.

        ```
        $ git clone https://github.com/li-rongzhi/TelegramChatbot.git```

2. **Create a Telegram Bot:**
    - Open Telegram and search for the "BotFather" to create a new bot.
    - Follow the instructions to create your bot and obtain the API token.
    - Create `.env` file and store the API token (please follow the format in `.env.example` file).
    - Please refer to the step-by-step guide on Telegram's official website [here](https://core.telegram.org/bots/features#creating-a-new-bot).

3. **Get an OpenAI API Key:**
    - Go to [OpenAI](https://openai.com/) and sign up or log in to your account.
    - Create a new API key and store in `.env` file.

4. **Get an News API Key:**
    - Go to [News API](https://newsapi.org/) and sign up or log in to your account.
    - Create a new API key and store in `.env` file.

5. **Set Up your MySQL Database:**
    - Create a database named `telebot`, whcih follows the configuration below.
    ```
        'host':'localhost',
        'user': 'root',
        'password': db_password,
        'database':'telebot'
    ```
    - Store the password required in `.env` file.

6. **Set Up a Public Domain for Webhook:**
    - Get a public domain which serve as the webhook.
    - You can make use of [`ngrok`](https://ngrok.com/) or other cloud service provider, forward your `localhost:3000` to the public domain.


## Deployment

After completing the set up instructions above, now you can deploy the chat bot.

1. **Create a Virtual Environment:**

    Create a Python virtual environment to isolate the project's dependencies. Navigate to the project directory and run the following commands:
    ```
    $ python -m venv venv
    ```

2. **Activate the Virtual Environment:**

    In MacOS:
    ```
    $ source venv/bin/activate
    ```
    In Windows:
    ```
    $ .\venv\Scripts\activate
    ```

3. **Install Dependencies:**

    Install any required dependencies for the project.
     ```
    $ pip install -r requirements.txt
    ```
    Notice: for `tensor-flow`, you may need to download the pacakge specific to your operating system.

4. **Run the Chatbot:**
    ```
    $ python app.py
    ```

5. **Access Your Bot:**

    Your bot is now running and accessible. Users can initiate a chat with the bot by searching for it on Telegram and starting a conversation.
