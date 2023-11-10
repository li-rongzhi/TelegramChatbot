# User Guide for Telegram Chatbot

Welcome to the Telegram Chatbot -- **[Jarvis](https://t.me/Rongzhi_chatbot)** ! This bot offers several exciting features to help you manage your tasks, chat with advanced Large Language Model (LLM), perform image style transfer, and stay updated with the latest news.

*Follow this simple guide to get started:*

1. **Initiate the Bot:**
   - To start using the chatbot, simply type `/start` in the chat.

2. **Task Management Mode:**
   - Type `/task` to enter Task Management mode.
   - In this mode, you can:
      - Add tasks to your to-do list:
         ```
         /add d/[task-description] t/[due-time] r/[remark]
         ```

         Note: `due-time` should follow this format: `yyyy-MM-dd hh-mm`
      - Mark tasks as complete:
         ```
         /mark [INDEX]
         ```
      - View your current tasks:
         ```
         /list
         ```
      - Delete completed tasks:
         ```
         /delete [INDEX]
         ```

3. **LLM Mode:**
   - Type `/llm` to enter LLM mode.
   - In this mode, you can:
      - Engage in text-based conversations with the `chatgpt-3.5-turbo` model empowered by OpenAI.
      - The chat bot supports context memory which enables smooth user experience. You can start a new dialog session with `/new`.
      - *Note*: there is a token limit for normal users, you can use `/upgrade` to upgrade to Premium for unlimited access.

4. **Style Transfer Mode:**
   - Type `/style_transfer` to enter Style Transfer mode.
   - In this mode, you can:
      - Select a style from a predefined style set and submit an image you want to transform using neural style transfer.
      - The bot will apply the chosen artistic style to your image and send you the result.

5. **News Feeding Mode:**
   - Type `/news` to enter News Feeding mode.
   - In this mode, you can:
      - Select a news category (e.g., Technology, Sports, Entertainment).
      - Receive the latest headlines from the chosen category.
      - Stay informed with the news that interests you the most.

6. **Timer Mode**:
   - Type `/timer` to enter Timer mode.
   - In this mode, you can:
      - Set a timer with given time period:
         ```
         /set [Time Period(Seconds)]
         ```
      - Unset the latest timer:
         ```
         /unset
         ```
      - *Note*: the chat bot supports at most one timer, if you try to set a new timer, the previous one will be deleted automatically.

6. **General Commands:**
   - Use `/back` to return to the `GENERAL` mode at any time.
   - Use `/help` for a quick reference of available commands and how to use them.
   - Use `/exit` to terminate a chat session.
   - Use `/upgrade` to upgrade to premium for unlimited llm access.

Please note that this chatbot is designed to assist you in different tasks, and each mode has its specific functionality. If you ever get stuck or need help, don't hesitate to use the `/help` command or reach out to the bot's developer for assistance.

Enjoy using the Telegram Chatbot and make the most of its features for task management, chat, image style transformation, and news updates!
