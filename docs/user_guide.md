# User Guide for Telegram Chatbot

Welcome to the Telegram Chatbot -- **[Jarvis](t.me/Rongzhi_chatbot)** ! This bot offers several exciting features to help you manage your tasks, chat with advanced Large Language Model (LLM), perform style transfers, and stay updated with the latest news.

*Follow this simple guide to get started:*

1. **Initiate the Bot:**
   - To start using the chatbot, simply type `/start` in the chat.

2. **Task Management Mode:**
   - Type `/task_management` to enter the Task Management mode.
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
     - Note: there is a token limit for normal users, you can use `/upgrade` to upgrade to Premium for unlimited access.

4. **Style Transfer Mode:**
   - Type `/style_transfer` to enter the Style Transfer mode.
   - In this mode, you can:
     - Select a style from a predefined style set and submit an image you want to transform using neural style transfer.
     - The bot will apply the chosen artistic style to your image and send you the result.

5. **News Updates:**
   - Type `/news` to enter the News mode.
   - In this mode, you can:
     - Select a news category (e.g., Technology, Sports, Entertainment).
     - Receive the latest headlines from the chosen category.
     - Stay informed with the news that interests you the most.

6. **General Commands:**
   - At any time, you can return to the main menu by typing `/back`.
   - Use `/help` for a quick reference of available commands and how to use them.
   - Use `/exit` to terminate a chat session.
   - Use `/upgrade` to upgrade to premium for unlimited llm access.

Please note that this chatbot is designed to assist you in different tasks, and each mode has its specific functionality. If you ever get stuck or need help, don't hesitate to use the `/help` command or reach out to the bot's support team for assistance.

Enjoy using the Telegram Chatbot and make the most of its features for task management, chat, style transformation, and news updates!
