import json
import discord
from asyncio import Semaphore
from re_edge_gpt import Chatbot
from src.bing_chat.response import send_message
from src.image.image_create import create_image

users_chatbot = {}

async def set_chatbot(user_id, cookies=None):
    if cookies:
        for cookie in cookies:
            if cookie["name"] == "_U":
                auth_cookie = cookie["value"]
                break
        users_chatbot[user_id] = UserChatbot(cookies=cookies, auth_cookie=auth_cookie, user_id=user_id)
    else:
        auth_cookie = None
        with open("./cookies.json", encoding="utf-8") as file:
            cookies_json = json.load(file)
            for cookie in cookies_json:
                if cookie["name"] == "_U":
                    auth_cookie = cookie["value"]
                    break
            users_chatbot[user_id] = UserChatbot(cookies=cookies_json, auth_cookie=auth_cookie, user_id=user_id)

def get_users_chatbot():
    return users_chatbot

def del_users_chatbot(user_id):
    del users_chatbot[user_id]
    
class UserChatbot():
    def __init__(self, cookies, auth_cookie, user_id):
        self.sem_send_message = Semaphore(1)
        self.sem_create_image = Semaphore(1)
        self.chatbot = Chatbot(cookies=cookies)
        self.thread = None
        self.conversation_style = "balanced"
        self.auth_cookie = auth_cookie
        self.user_id = user_id
    
    def set_conversation_style(self, conversation_style: str):
        self.conversation_style = conversation_style
    
    def get_conversation_style(self) -> str:
        return self.conversation_style
    
    def set_thread(self, thread: discord.threads.Thread):
        self.thread = thread
    
    def get_thread(self) -> discord.threads.Thread:
        return self.thread

    async def send_message(self, message: str, interaction: discord.Interaction=None, image: str=None):
        if not self.sem_send_message.locked():
            async with self.sem_send_message:
                if interaction:
                    if interaction.type == discord.InteractionType.component or self.thread == None:
                        await send_message(self.chatbot, message, image, self.conversation_style, users_chatbot, self.user_id, interaction=interaction)
                else:
                    await send_message(self.chatbot, message, image, self.conversation_style, users_chatbot, self.user_id, thread=self.thread)
        else:
            if interaction:
                if not interaction.response.is_done():
                    await interaction.response.defer(thinking=True)
                await interaction.followup.send("> **ERROE: Please wait for the previous command to complete.**")
            else:
                await self.thread.send("> **ERROE: Please wait for the previous command to complete.**")

    async def create_image(self, interaction: discord.Interaction, prompt: str):
        if not self.sem_create_image.locked():
            async with self.sem_create_image:
                await create_image(interaction, users_chatbot, prompt, self.auth_cookie)
        else:
            if not interaction.response.is_done():
                await interaction.response.defer(thinking=True)
            await interaction.followup.send("> **ERROE: Please wait for the previous command to complete.**")

    
    async def reset_conversation(self):
        await self.chatbot.reset()