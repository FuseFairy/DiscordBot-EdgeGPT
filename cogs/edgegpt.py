import discord
import asyncio
from EdgeGPT import Chatbot
from discord.ext import commands
from core.classes import Cog_Extension
from src import log
from src.response import send_message
from dotenv import load_dotenv

load_dotenv()

bot = commands.Bot(command_prefix='!', intents = discord.Intents.all())
chatbot = Chatbot("./cookies.json")
logger = log.setup_logger(__name__)
conversation_style = "balanced" # default conversation style

# switch conversation style
async def switch_style(style: str):
    global conversation_style
    conversation_style = style

class edgegpt(Cog_Extension):
    @bot.tree.command(name = "bing", description = "Have a chat with Bing")
    async def bing(self, interaction: discord.Interaction, *, message: str):
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

    # switch conversation style to creative
    @bot.tree.command(name="style_creative", description="Switch conversation style to creative")
    async def switch_style_creative(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        await switch_style("creative")
        await interaction.followup.send("> **Info: successfull switch conversation style to creative.**")
        logger.warning("\x1b[31mConversation style has been successfully switch to creative\x1b[0m")

    # switch conversation style to balanced
    @bot.tree.command(name="style_balanced", description="Switch conversation style to balanced")
    async def switch_style_balanced(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        await switch_style("balanced")
        await interaction.followup.send("> **Info: successfull switch conversation style to balanced.**")
        logger.warning("\x1b[31mConversation style has been successfully switch to balanced\x1b[0m")

    # switch conversation style to precise
    @bot.tree.command(name="style_precise", description="Switch conversation style to precise")
    async def switch_style_precise(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        await switch_style("precise")
        await interaction.followup.send("> **Info: successfull switch conversation style to precise.**")
        logger.warning("\x1b[31mConversation style has been successfully switch to precise\x1b[0m")

async def setup(bot):
    await bot.add_cog(edgegpt(bot))