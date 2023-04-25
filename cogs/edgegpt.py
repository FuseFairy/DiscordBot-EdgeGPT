import discord
from EdgeGPT import Chatbot
from discord.ext import commands
from discord import app_commands
from core.classes import Cog_Extension
from src import log
from src.response import send_message, get_func_status, set_func_status

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
logger = log.setup_logger(__name__)
users_chatbot = {}
user_conversation_style = {}

class UserChatbot:
    def __init__(self, cookie_path, user_id):
        self.chatbot = Chatbot(cookie_path=cookie_path)
        user_conversation_style[user_id] = "balanced"
        self.user_id = user_id

    async def send_message(self, interaction, message, conversation_style):
        await send_message(self.chatbot, interaction, message, conversation_style)

    async def reset(self):
        self.chatbot.reset()

class EdgeGPT(Cog_Extension):
    # Chat with Bing
    @bot.tree.command(name="bing", description="Have a chat with Bing")
    async def bing(self, interaction: discord.Interaction, *, message: str):
        try:
            using = await get_func_status(interaction.user.id)
        except:
            await set_func_status(interaction.user.id, False)
            using = await get_func_status(interaction.user.id)
        if not using:
            await interaction.response.defer(ephemeral=False, thinking=True)
            username = str(interaction.user)
            usermessage = message
            channel = str(interaction.channel)
            user_id = interaction.user.id
            if user_id not in users_chatbot:
                # create a new chatbot instance for this user
                users_chatbot[user_id] = UserChatbot(cookie_path="./cookies.json", user_id=interaction.user.id)
            conversation_style = user_conversation_style[interaction.user.id]
            logger.info(f"\x1b[31m{username}\x1b[0m : '{usermessage}' ({channel}) [Style: {conversation_style}]")
            await users_chatbot[user_id].send_message(interaction, usermessage, conversation_style)
        else:
            await interaction.response.defer(ephemeral=True, thinking=True)
            await interaction.followup.send("Please wait for your last conversation to finish.")

    # Reset Bing conversation history
    @bot.tree.command(name="reset", description="Complete reset Bing conversation history")
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
    @bot.tree.command(name="switch_style", description="Switch conversation style")
    @app_commands.choices(style=[app_commands.Choice(name="Creative", value="creative"), app_commands.Choice(name="Balanced", value="balanced"), app_commands.Choice(name="Precise", value="precise")])
    async def switch_style(self, interaction: discord.Interaction, style: app_commands.Choice[str]):
        await interaction.response.defer(ephemeral=True, thinking=True)
        user_conversation_style[interaction.user.id] = style.value
        await interaction.followup.send(f"> **Info: successfull switch conversation style to {style.value}.**")
        logger.warning(f"\x1b[31mConversation style has been successfully switch to {style.value}\x1b[0m")

async def setup(bot):
    await bot.add_cog(EdgeGPT(bot))
