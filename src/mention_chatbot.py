import json
import os
from .log import setup_logger
from re_edge_gpt import Chatbot

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
            if not os.path.exists("./cookies.json"):
                logger.error("cookies.json file not found")
                return
            if cookies == None:
                with open("./cookies.json", encoding="utf-8") as file:
                    cookies = json.load(file)
            self.chatbot = await Chatbot.create(cookies=cookies, mode="Bing")
        except Exception as e:
            logger.error(e, exc_info=True)
    
    async def reset(self):
        await self.chatbot.reset()

client = MentionChatbot()

def get_client():
    return client