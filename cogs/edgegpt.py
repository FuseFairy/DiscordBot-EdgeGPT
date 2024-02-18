import discord
import json
import os
from typing import Optional
from discord import app_commands
from core.classes import Cog_Extension
from src.log import setup_logger
from src.user_chatbot import set_chatbot, get_users_chatbot
from dotenv import load_dotenv

load_dotenv()

logger = setup_logger(__name__)

class EdgeGPT(Cog_Extension):
    cookies_group = app_commands.Group(name="cookies", description="set personal cookies")
    create_group = app_commands.Group(name="create", description="Create images.")
    reset_group = app_commands.Group(name="reset", description="Reset conversation.")

    @cookies_group.command(name="setting", description="can set personal Copilot cookies and auth_cookie(for create image), no mandatory setting.")
    async def cookies_setting(self, interaction: discord.Interaction, cookies_file: Optional[discord.Attachment]=None, auth_cookie: str=None):
        await interaction.response.defer(thinking=True)
        allowed_channel_id = os.getenv("SETTING_CHANNEL_ID")
        if allowed_channel_id and int(allowed_channel_id) != interaction.channel_id:
            await interaction.followup.send(f"> **Command can only used on <#{allowed_channel_id}>**")
            return
        user_id = interaction.user.id
        try:
            if cookies_file or auth_cookie:
                if cookies_file:
                    if "json" in cookies_file.content_type or "text" in cookies_file.content_type:
                        cookies = json.loads(await cookies_file.read())
                        is_copilot = False
                        for cookie in cookies:
                            if cookie["domain"] == "copilot.microsoft.com":
                                is_copilot=True
                                break
                        if not is_copilot:
                            await interaction.followup.send("> **ERROR：Cookies are wrong, please copy cookies from https://copilot.microsoft.com/**")
                            return
                        await set_chatbot(user_id=user_id, cookies=cookies)
                        await interaction.followup.send("> **INFO：You have successfully set copilot cookies!**")
                        logger.info(f"{interaction.user}：setting copilot cookies succeeded")
                    else:
                        await interaction.followup.send("> **ERROR： cookies_file only Support json or txt format only.**")
                if auth_cookie:
                    await set_chatbot(user_id=user_id, auth_cookie=auth_cookie)
                    try:
                        await interaction.followup.send("> **INFO：You have successfully set auth_cookie!**")
                    except:
                        await interaction.followup.send("> **INFO：You have successfully set auth_cookie!**")
                    logger.info(f"{interaction.user}：setting auth_cookie succeeded")
            else:
                await interaction.followup.send(f">>> **ERROR：Please upload a file(.json or .txt) containing Copilot cookies or input your auth_cookie**")
        except Exception as e:
            await interaction.followup.send(f">>> **ERROR：{e}**")

    # Chat with Copilot.
    @app_commands.command(name="copilot", description="Create thread for conversation.")
    @app_commands.choices(version=[app_commands.Choice(name="default", value="default"), app_commands.Choice(name="jail_break", value="jailbreak")])
    @app_commands.choices(style=[app_commands.Choice(name="Creative", value="creative"), app_commands.Choice(name="Balanced", value="balanced"), app_commands.Choice(name="Precise", value="precise")])
    @app_commands.choices(type=[app_commands.Choice(name="private", value="private"), app_commands.Choice(name="public", value="public")])
    async def chat(self, interaction: discord.Interaction, version: app_commands.Choice[str], style: app_commands.Choice[str], type: app_commands.Choice[str]):
        await interaction.response.defer(thinking=True)
        allowed_channel_id = os.getenv("CHAT_CHANNEL_ID")
        if allowed_channel_id and int(allowed_channel_id) != interaction.channel_id:
            await interaction.followup.send(f"> **Command can only used on <#{allowed_channel_id}>**")
            return
        if isinstance(interaction.channel, discord.Thread):
            await interaction.followup.send("This command is disabled in thread.")
            return
        
        user_id = interaction.user.id
        try:
            await set_chatbot(user_id=user_id, conversation_style=style.value, version=version.value)
        except Exception as e:
            await interaction.followup.send(f">>> **ERROR：{e}**")
            return

        users_chatbot = get_users_chatbot()

        thread = users_chatbot[user_id].get_thread()
        if thread:
            await users_chatbot[user_id].reset_conversation()
            try:
                await thread.delete()
            except:
                pass
        if type.value == "private":
            type = discord.ChannelType.private_thread
        else:
            type = discord.ChannelType.public_thread
        thread = await interaction.channel.create_thread(name=f"{interaction.user.name} chatroom", type=type)
        users_chatbot[user_id].set_thread(thread)
        await interaction.followup.send(f"here is your thread {thread.jump_url}")
        
    # Create images.
    @create_group.command(name="image", description="Generate image by Bing Image Creator")
    async def create_image(self, interaction: discord.Interaction, *, prompt: str):
        await interaction.response.defer(thinking=True)
        allowed_channel_id = os.getenv("CREATE_IMAGE_CHANNEL_ID")
        if allowed_channel_id and int(allowed_channel_id) != interaction.channel_id:
            await interaction.followup.send(f"> **Command can only used on <#{allowed_channel_id}>**")
            return
        users_chatbot = get_users_chatbot()
        user_id = interaction.user.id
        if user_id not in users_chatbot:
            await set_chatbot(user_id=user_id)
        await users_chatbot[user_id].create_image(interaction, prompt)
    
    # Reset conversation
    @reset_group.command(name="conversation", description="Reset bing chatbot conversation.")
    async def reset_conversation(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        allowed_channel_id = os.getenv("RESET_CHAT_CHANNEL_ID")
        if allowed_channel_id and int(allowed_channel_id) != interaction.channel_id:
            await interaction.followup.send(f"> **Command can only used on <#{allowed_channel_id}>**")
            return
        users_chatbot = get_users_chatbot()
        user_id = interaction.user.id
        
        if user_id not in users_chatbot or users_chatbot[user_id].get_chatbot() == None:
            await interaction.followup.send(f">>> **ERROR：You don't have any conversation yet.**")
            return
        try:
            await users_chatbot[user_id].reset_conversation()
            await interaction.followup.send("> **INFO：Reset finish.**")
        except Exception as e:
            await interaction.followup.send(f">>> **ERROR：{e}**")
        
async def setup(bot):
    await bot.add_cog(EdgeGPT(bot))