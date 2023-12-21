import discord
import json
from typing import Optional
from discord import app_commands
from core.classes import Cog_Extension
from src import log
from src.user_chatbot import set_chatbot, get_users_chatbot, del_users_chatbot

logger = log.setup_logger(__name__)

class EdgeGPT(Cog_Extension):
    chatbot_group = app_commands.Group(name="chatbot", description="Bing setting.")
    switch_group = app_commands.Group(name="switch", description="Switch conversation style.")
    create_group = app_commands.Group(name="create", description="Create images.")
    reset_group = app_commands.Group(name="reset", description="Reset conversation.")

    # Set or delete Bing chatbot.
    @chatbot_group.command(name="setting", description="Set or delete bing chatbot.")
    @app_commands.choices(choice=[app_commands.Choice(name="set", value="set"), app_commands.Choice(name="delete", value="delete")])
    async def cookies_setting(self, interaction: discord.Interaction, choice: app_commands.Choice[str], cookies_file: Optional[discord.Attachment]=None):
        """Set or delete Bing chatbot.
            
            Parameters
            -----------
            choice: Choice[str]
                Remember to upload your bing cookie if you want to use your own bing account when you choose to set it up.
        """

        await interaction.response.defer(ephemeral=True, thinking=True)
        user_id = interaction.user.id
        if choice.value == "set":
            try:
                if cookies_file is not None:
                    if "json" in cookies_file.content_type:
                        cookies = json.loads(await cookies_file.read())
                        await set_chatbot(user_id, cookies)
                        await interaction.followup.send("> **INFO: Chatbot set successful!**")
                        logger.info(f"{interaction.user} set Bing Chatbot successful")
                    else:
                        await interaction.followup.send("> **ERROR: Support json format only.**")
                else:
                    await set_chatbot(user_id)
                    await interaction.followup.send("> **INFO: Chatbot set successful! (using bot owner cookies)**")
                    logger.info(f"{interaction.user} set Bing chatbot successful. (using bot owner cookies)")
            except Exception as e:
                await interaction.followup.send(f">>> **ERROR: {e}**")
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
    async def bing(self, interaction: discord.Interaction, image: Optional[discord.Attachment]=None, *, message: str):
        users_chatbot = get_users_chatbot()
        username = interaction.user
        usermessage = message
        channel = interaction.channel
        user_id = interaction.user.id
        if user_id not in users_chatbot:
            await interaction.response.send_message("> **ERROE: Please use  `/chatbot setting`   to set yourself Bing chatbot first.**", ephemeral=True)
        # Check if an attachment is provided
        if image is  None or "image" in image.content_type:
            logger.info(f"{username}: {usermessage} ({channel}) [Style: {users_chatbot[user_id].get_conversation_style()}]")
            await users_chatbot[user_id].send_message(interaction, usermessage, image)
        else:
            await interaction.response.send_message("> **ERROE: This file format is not supported.**", ephemeral=True)
        
    # Switch conversation style.
    @switch_group.command(name="style", description="Switch conversation style")
    @app_commands.choices(style=[app_commands.Choice(name="Creative", value="creative"), app_commands.Choice(name="Balanced", value="balanced"), app_commands.Choice(name="Precise", value="precise")])
    async def switch_style(self, interaction: discord.Interaction, style: app_commands.Choice[str]):
        await interaction.response.defer(ephemeral=True, thinking=True)
        users_chatbot = get_users_chatbot()
        user_id = interaction.user.id
        if user_id not in users_chatbot:
            await interaction.followup.send("> **ERROR: Please use  ` /chatbot setting`   to set yourself Bing chatbot first.**")
        users_chatbot[user_id].set_conversation_style(style.value)
        await interaction.followup.send(f"> **INFO: successfull switch conversation style to {style.value}.**")
        
    # Create images.
    @create_group.command(name="image", description="Generate image by Bing image creator")
    async def create_image(self, interaction: discord.Interaction, *, prompt: str):
        users_chatbot = get_users_chatbot()
        user_id = interaction.user.id
        if user_id not in users_chatbot:
            await interaction.response.defer(ephemeral=True, thinking=True)
            await interaction.followup.send("> **ERROR: Please use  ` /chatbot setting`   to set yourself Bing chatbot first.**")
        await interaction.response.defer(ephemeral=False, thinking=True)
        await users_chatbot[user_id].create_image(interaction, prompt)
    
    # Reset conversation
    @reset_group.command(name="conversation", description="Reset bing chatbot conversation.")
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