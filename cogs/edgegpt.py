import discord
import json
from typing import Optional
from ImageGen import ImageGenAsync
from EdgeGPT import Chatbot
from discord import app_commands
from core.classes import Cog_Extension
from src import log
from src.imageCreate import create_image, get_using_create, set_using_create
from src.response import send_message, get_using_send, set_using_send

logger = log.setup_logger(__name__)

users_chatbot = {}
users_image_generator = {}
user_conversation_style = {}

class UserChatbot:
    def __init__(self, cookies):
        self.chatbot = Chatbot(cookies=cookies)

    async def send_message(self, interaction, message, conversation_style):
        await send_message(self.chatbot, interaction, message, conversation_style)

    async def create_image(self, interaction, prompt: str, image_generator):
        await create_image(interaction, prompt, image_generator)

    async def reset(self):
        await self.chatbot.reset()

class EdgeGPT(Cog_Extension):
    # Chat with Bing
    @app_commands.command(name="bing", description="Have a chat with Bing")
    async def bing(self, interaction: discord.Interaction, *, message: str):
        try:
            using = await get_using_send(interaction.user.id)
        except:
            await set_using_send(interaction.user.id, False)
            using = await get_using_send(interaction.user.id)
        if not using: 
            username = str(interaction.user)
            usermessage = message
            channel = str(interaction.channel)
            user_id = interaction.user.id
            if user_id not in users_chatbot:
                await interaction.response.defer(ephemeral=True, thinking=True)
                await interaction.followup.send("> **Please use */bing_cookies* command to set your bing cookies first**")
            else:
                await interaction.response.defer(ephemeral=False, thinking=True)
                conversation_style = user_conversation_style[user_id]
                logger.info(f"\x1b[31m{username}\x1b[0m : '{usermessage}' ({channel}) [Style: {conversation_style}]")
                await users_chatbot[user_id].send_message(interaction, usermessage, conversation_style)
        else:
            await interaction.response.defer(ephemeral=True, thinking=True)
            await interaction.followup.send("> **Please wait for your last conversation to finish.**")

    # Reset Bing conversation history
    @app_commands.command(name="reset", description="Complete reset Bing conversation history")
    async def reset(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            await users_chatbot[interaction.user.id].reset()
            await interaction.followup.send("> **Info: Reset finish.**")
            logger.warning("\x1b[31mBing has been successfully reset\x1b[0m")
        except:
            await interaction.followup.send(f"> **Info: You don't have any conversation yet.**")
            logger.exception("Bing reset failed.")

    # Switch conversation style
    @app_commands.command(name="switch_style", description="Switch conversation style")
    @app_commands.choices(style=[app_commands.Choice(name="Creative", value="creative"), app_commands.Choice(name="Balanced", value="balanced"), app_commands.Choice(name="Precise", value="precise")])
    async def switch_style(self, interaction: discord.Interaction, style: app_commands.Choice[str]):
        await interaction.response.defer(ephemeral=True, thinking=True)
        user_conversation_style[interaction.user.id] = style.value
        await interaction.followup.send(f"> **Info: successfull switch conversation style to {style.value}.**")
        logger.warning(f"\x1b[31mConversation style has been successfully switch to {style.value}\x1b[0m")
    
    # Set and delete bing cookies
    @app_commands.command(name="bing_cookies", description="Set or delete bing cookies")
    @app_commands.choices(choice=[app_commands.Choice(name="set", value="set"), app_commands.Choice(name="delete", value="delete")])
    async def cookies_setting(self, interaction: discord.Interaction, choice: app_commands.Choice[str], cookies_file: Optional[discord.Attachment]=None):
        await interaction.response.defer(ephemeral=True, thinking=True)
        if choice.value == "set":
            try:
                content = json.loads(await cookies_file.read())
                for cookie in content:
                    if cookie.get("name") == "_U":
                        auth_cookie = cookie.get("value")
                        break
                users_image_generator[interaction.user.id] = ImageGenAsync(auth_cookie, quiet=True)
                users_chatbot[interaction.user.id] = UserChatbot(cookies=content)
                user_conversation_style[interaction.user.id] = "balanced" 
                await interaction.followup.send("> **Upload successful!**")
                logger.warning(f"\x1b[31m{interaction.user} set bing cookies successful\x1b[0m")
            except:
                await interaction.followup.send("> **Please upload your cookies.**")
        else:
            try:
                del users_chatbot[interaction.user.id]
                del users_image_generator[interaction.user.id]
                del user_conversation_style[interaction.user.id]
                await interaction.followup.send("> **Delete finish.**")
                logger.warning(f"\x1b[31m{interaction.user} delete cookies\x1b[0m")
            except:
                await interaction.followup.send("> **You haven't set up Bing cookies.**")

    # Create images
    @app_commands.command(name = "create_image", description = "generate image by bing image creator")
    async def create_image(self, interaction: discord.Interaction, *, prompt: str):
        if interaction.user.id not in users_image_generator:
            await interaction.response.defer(ephemeral=True, thinking=True)
            await interaction.followup.send("> **Please use */bing_cookies* command to set your bing cookies first.**")
        else:
            try:
                using = await get_using_create(interaction.user.id)
            except:
                await set_using_create(interaction.user.id, False)
                using = await get_using_create(interaction.user.id)
            if not using: 
                logger.info(f"\x1b[31m{interaction.user}\x1b[0m : '{prompt}' ({interaction.channel}) [BingImageCreator]")
                await users_chatbot[interaction.user.id].create_image(interaction, prompt, users_image_generator[interaction.user.id])
            else:
                await interaction.response.defer(ephemeral=True, thinking=True)
                await interaction.followup.send("> **Please wait for your last image to create finish.**")

async def setup(bot):
    await bot.add_cog(EdgeGPT(bot))