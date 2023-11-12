import discord
import json
from typing import Optional
from discord import app_commands
from core.classes import Cog_Extension
from src import log
from src.user_chatbot import set_chatbot, get_users_chatbot, del_users_chatbot

logger = log.setup_logger(__name__)

class EdgeGPT(Cog_Extension):
    # Set or delete Bing chatbot.
    @app_commands.command(name="bing_setting", description="Set or delete bing chatbot.")
    @app_commands.choices(choice=[app_commands.Choice(name="set", value="set"), app_commands.Choice(name="delete", value="delete")])
    async def cookies_setting(self, interaction: discord.Interaction, choice: app_commands.Choice[str], cookies_file: Optional[discord.Attachment]=None):
        await interaction.response.defer(ephemeral=True, thinking=True)
        user_id = interaction.user.id
        if choice.value == "set":
            if cookies_file is not None:
                cookies = json.loads(await cookies_file.read())
                await set_chatbot(user_id, cookies)
                await interaction.followup.send("> **INFO: Chatbot set successful!**")
                logger.info(f"{interaction.user} set Bing Chatbot successful")
            else:
                await set_chatbot(user_id)
                await interaction.followup.send("> **INFO: Chatbot set successful! (using bot owner cookies)**")
                logger.info(f"{interaction.user} set Bing chatbot successful. (using bot owner cookies)")
        else:
            users_chatbot = get_users_chatbot()
            if user_id in users_chatbot:
                del_users_chatbot(user_id)
                await interaction.followup.send("> **INFO: Delete your Bing chatbot completely.**")
                logger.info(f"Delete {interaction.user} Cookies.")
            else:
                await interaction.followup.send("> **ERROR: You don't have any Bing chatbot yet.**")

    # Chat with Bing.
    @app_commands.command(name="bing", description="Have a chat with Bing")
    async def bing(self, interaction: discord.Interaction, *, message: str):
        users_chatbot = get_users_chatbot()
        username = interaction.user
        usermessage = message
        channel = interaction.channel
        user_id = interaction.user.id
        if user_id not in users_chatbot:
            await interaction.response.defer(ephemeral=True, thinking=True)
            await interaction.followup.send("> **ERROE: Please use  ` /chatbot_setting`   to set yourself Bing chatbot first.**")
        logger.info(f"{username}: {usermessage} ({channel}) [Style: {users_chatbot[user_id].get_conversation_style()}]")
        await users_chatbot[user_id].send_message(interaction, usermessage)

    # Switch conversation style.
    @app_commands.command(name="switch_style", description="Switch conversation style")
    @app_commands.choices(style=[app_commands.Choice(name="Creative", value="creative"), app_commands.Choice(name="Balanced", value="balanced"), app_commands.Choice(name="Precise", value="precise")])
    async def switch_style(self, interaction: discord.Interaction, style: app_commands.Choice[str]):
        await interaction.response.defer(ephemeral=True, thinking=True)
        users_chatbot = get_users_chatbot()
        user_id = interaction.user.id
        if user_id not in users_chatbot:
            await interaction.followup.send("> **ERROR: Please use  ` /chatbot_setting`   to set yourself Bing chatbot first.**")
        users_chatbot[user_id].set_conversation_style(style.value)
        await interaction.followup.send(f"> **INFO: successfull switch conversation style to {style.value}.**")
        
    # Create images.
    @app_commands.command(name="create_image", description="generate image by Bing image creator")
    async def create_image(self, interaction: discord.Interaction, *, prompt: str):
        users_chatbot = get_users_chatbot()
        user_id = interaction.user.id
        if user_id not in users_chatbot:
            await interaction.response.defer(ephemeral=True, thinking=True)
            await interaction.followup.send("> **ERROR: Please use  ` /chatbot_setting`   to set yourself Bing chatbot first.**")
        await interaction.response.defer(ephemeral=False, thinking=True)
        await users_chatbot[user_id].create_image(interaction, prompt)
    
    # Reset conversation
    @app_commands.command(name="reset_conversation", description="Reset bing chatbot conversation.")
    async def reset_conversation(self, interaction: discord.Interaction):
        users_chatbot = get_users_chatbot()
        user_id = interaction.user.id
        if user_id not in users_chatbot:
            await interaction.response.defer(ephemeral=True, thinking=True)
            await interaction.followup.send("> **ERROR: Please use  ` /chatbot_setting`   to set yourself Bing chatbot first.**")
        await interaction.response.defer(ephemeral=True, thinking=True)
        await users_chatbot[user_id].reset_conversation()
        await interaction.followup.send(f"> **Info: Reset finish.**")
        

async def setup(bot):
    await bot.add_cog(EdgeGPT(bot))