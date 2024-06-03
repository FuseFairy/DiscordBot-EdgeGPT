import json
import os
import asyncio
from .log import setup_logger
from re_edge_gpt import Chatbot
from dotenv import load_dotenv
from src.auto_cookies import refresh_cookies

load_dotenv()
logger = setup_logger(__name__)

class MentionChatbot():
    def __init__(self):
        self.conversation_style = "balanced"
        self.chatbot: Chatbot = None
    
    def set_conversation_style(self, conversation_style):
        self.conversation_style = conversation_style

    def get_conversation_style(self):
        return self.conversation_style

    async def set_chatbot(self, cookies: str=None):
        try:
            if cookies == None:
                if os.getenv("BING_COOKIES"):
                    cookies = json.loads(os.getenv("BING_COOKIES"))
                elif os.path.exists("./cookies.json"):
                    with open("./cookies.json", encoding="utf-8") as file:
                        cookies = json.load(file)
            
            if os.getenv("AUTO_COOKIES") == "True":
                if os.getenv("AUTO_COOKIES"):       
                    asyncio.create_task(refresh_cookies())
                elif not os.path.exists("./cookies.json") and not os.getenv("BING_COOKIES"):
                    logger.error("Please setup your Bing cookies.")
                    return

            self.chatbot = await Chatbot.create(proxy=os.getenv("PROXY"), cookies=cookies, mode="Bing")
        except Exception as e:
            logger.error(e, exc_info=True)
    
    async def reset(self):
        await self.chatbot.reset()

client = MentionChatbot()

def get_client():
    return client