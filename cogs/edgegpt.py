import discord
import asyncio
from EdgeGPT import Chatbot
from discord.ext import commands
from discord import app_commands
from core.classes import Cog_Extension
from src import log
from src.response import send_message

bot = commands.Bot(command_prefix='!', intents = discord.Intents.all())
chatbot = Chatbot("./cookies.json")
logger = log.setup_logger(__name__)
conversation_style = "balanced" # default conversation style

class edgegpt(Cog_Extension):
    # chat with Bing
    @bot.tree.command(name = "bing", description = "Have a chat with Bing")
    async def bing(self, interaction: discord.Interaction, *, message: str):
        await interaction.response.defer(ephemeral=False, thinking=True)
        if interaction.user == bot.user:
            return
        username = str(interaction.user)
        usermessage = message
        channel = str(interaction.channel)
        logger.info(f"\x1b[31m{username}\x1b[0m : '{usermessage}' ({channel}) [Style: {conversation_style}]")
        task = asyncio.create_task(send_message(chatbot, interaction, usermessage, conversation_style))
        await asyncio.gather(task)

    # reset Bing conversation history
    @bot.tree.command(name="reset", description="Complete reset Bing conversation history")
    async def reset(self, interaction: discord.Interaction):
        open('discord_bot.log', 'w').close()
        await interaction.response.defer(ephemeral=False)
        await chatbot.reset()
        await interaction.followup.send("> **Info: Reset finish.**")
        logger.warning("\x1b[31mBing has been successfully reset\x1b[0m")

    # switch conversation style
    @bot.tree.command(name="switch_style", description="Switch conversation style")
    @app_commands.choices(style=[app_commands.Choice(name="Creative", value="creative"), app_commands.Choice(name="Balanced", value="balanced"), app_commands.Choice(name="Precise", value="precise")])
    async def switch_style(self, interaction: discord.Interaction, style: app_commands.Choice[str]):
        await interaction.response.defer(ephemeral=False)
        global conversation_style
        conversation_style = style.value
        await interaction.followup.send(f"> **Info: successfull switch conversation style to {conversation_style}.**")
        logger.warning(f"\x1b[31mConversation style has been successfully switch to {conversation_style}\x1b[0m")

async def setup(bot):
    await bot.add_cog(edgegpt(bot))
