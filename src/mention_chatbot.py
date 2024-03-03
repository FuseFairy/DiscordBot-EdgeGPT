import json
import os
from re_edge_gpt import Chatbot

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
            if cookies == None and os.path.isfile("./cookies.json"):
                with open("./cookies.json", encoding="utf-8") as file:
                    cookies = json.load(file)
            self.chatbot = await Chatbot.create(cookies=cookies, mode="Bing")
        except:
            return
    
    def get_chatbot(self):
        return self.chatbot
    
    async def reset(self):
        await self.chatbot.reset()

client = MentionChatbot()

def get_client():
    return client