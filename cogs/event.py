import discord
import re
import os
import asyncio
from re_edge_gpt import ConversationStyle
from dotenv import load_dotenv
from discord.ext import commands
from core.classes import Cog_Extension
from functools import partial
from src.log import setup_logger
from src.user_chatbot import get_users_chatbot
from src.mention_chatbot import get_client

load_dotenv()

try:
    MENTION_CHANNEL_ID = int(os.getenv("MENTION_CHANNEL_ID"))
except:
    MENTION_CHANNEL_ID = None
logger = setup_logger(__name__)
sem = asyncio.Semaphore(1)

# To add suggest responses
class ButtonView(discord.ui.View):
    def __init__(self, suggest_responses:list):
        super().__init__(timeout=120)
        self.client = get_client()
        self.conversation_style_str = self.client.get_conversation_style()
        self.chatbot = self.client.get_chatbot()
        # Add buttons
        for label in suggest_responses:
            button = discord.ui.Button(label=label)
            # Button event
            async def callback(interaction: discord.Interaction, button: discord.ui.Button):
                    await interaction.response.defer(ephemeral=False, thinking=True)
                    username = str(interaction.user)
                    usermessage = button.label
                    channel = str(interaction.channel)
                    logger.info(f"\x1b[31m{username}\x1b[0m : '{usermessage}' ({channel}) [Style: {self.conversation_style_str}] [button]")
                    await send_message(interaction, self.chatbot, self.conversation_style_str, usermessage)
            self.add_item(button)
            self.children[-1].callback = partial(callback, button=button)

# Show Dropdown
class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        self.client = get_client()

        options = [
            discord.SelectOption(label="Creative", description="Switch conversation style to Creative", emoji='🎨'),
            discord.SelectOption(label="Balanced", description="Switch conversation style to Balanced", emoji='⚖️'),
            discord.SelectOption(label="Precise", description="Switch conversation style to Precise", emoji='🔎'),
            discord.SelectOption(label="Reset", description="Reset conversation", emoji="🔄")
        ]

        dropdown = discord.ui.Select(
            placeholder="Choose setting",
            min_values=1,
            max_values=1,
            options=options
        )

        dropdown.callback = self.dropdown_callback
        self.add_item(dropdown)
    # Dropdown event
    async def dropdown_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False, thinking=True)
        await self.client.reset()
        if interaction.data['values'][0] == "Creative":
            self.client.set_conversation_style("creative")
            await interaction.followup.send(f"> **Info: successfull switch conversation style to *{interaction.data['values'][0]}*.**")
            logger.warning(f"\x1b[31mConversation style has been successfully switch to {interaction.data['values'][0]}\x1b[0m")
        elif interaction.data['values'][0] == "Balanced":
            self.client.set_conversation_style("balanced")
            await interaction.followup.send(f"> **Info: successfull switch conversation style to *{interaction.data['values'][0]}*.**")
            logger.warning(f"\x1b[31mConversation style has been successfully switch to {interaction.data['values'][0]}\x1b[0m")
        elif interaction.data['values'][0] == "Precise":
            self.client.set_conversation_style("precise")
            await interaction.followup.send(f"> **Info: successfull switch conversation style to *{interaction.data['values'][0]}*.**")
            logger.warning(f"\x1b[31mConversation style has been successfully switch to {interaction.data['values'][0]}\x1b[0m")
        else:
            await self.client.reset()
            await interaction.followup.send(f"> **Info: Reset finish.**")
            logger.warning("\x1b[31mBing has been successfully reset\x1b[0m")
        # disable dropdown after select
        for dropdown in self.children:
            dropdown.disabled = True
        await interaction.followup.edit_message(message_id=interaction.message.id, view=self)

async def send_message(interaction, chatbot, conversation_style_str, user_message: str, image: str=None):
    async with sem:
        reply = ''
        text = ''
        link_embed = ''
        all_url = []

        if isinstance(interaction, discord.Interaction) and not interaction.response.is_done():
            await interaction.response.defer(ephemeral=False, thinking=True)

        try:
            # Change conversation style
            if conversation_style_str == "creative":
                conversation_style=ConversationStyle.creative
            elif conversation_style_str == "precise":
                conversation_style=ConversationStyle.precise
            else:
                conversation_style=ConversationStyle.balanced

            reply = await chatbot.ask(
                prompt=user_message,
                conversation_style=conversation_style,
                simplify_response=True,
                attachment={"image_url":f"{image}"}
            )

            # Get reply text
            text = f"{reply['text']}"
            text = re.sub(r'\[\^(\d+)\^\]',  '', text)
            text = re.sub(r':\s*\[[^\]]*\]\([^\)]*\)', '', text)
            text = re.sub(r'<[^>]*>', '', text)
            
            # Get the URL, if available
            urls = re.findall(r'\[(\d+)\. (.*?)\]\((https?://.*?)\)', reply["sources_link"])
            if len(urls) > 0:
                for url in urls:
                    all_url.append(f"{url[0]}. [{url[1]}]({url[2]})")
                link_text = "\n".join(all_url)
                link_embed = discord.Embed(description=link_text)
            
            # Set the final message
            response = f"{text} \n(***style: {conversation_style_str}***)"
            
            # Discord limit about 2000 characters for a message
            while len(response) > 2000:
                temp = response[:2000]
                response = response[2000:]
                if isinstance(interaction, discord.Interaction):
                    await interaction.followup.send(temp)
                elif isinstance(interaction, discord.message.Message):
                    await interaction.channel.send(temp)
                
            suggest_responses = reply["suggestions"]              
            if link_embed:
                if isinstance(interaction, discord.Interaction):
                    await interaction.followup.send(response, view=ButtonView(suggest_responses), embed=link_embed, wait=True)
                elif isinstance(interaction, discord.message.Message):
                    await interaction.channel.send(response, view=ButtonView(suggest_responses), embed=link_embed)
            else:
                if isinstance(interaction, discord.Interaction):
                    await interaction.followup.send(response, view=ButtonView(suggest_responses), wait=True)
                elif isinstance(interaction, discord.message.Message):
                    await interaction.channel.send(response, view=ButtonView(suggest_responses))

        except Exception as e:
            if isinstance(interaction, discord.Interaction):
                await interaction.followup.send(f">>> **Error：{e}**")
            elif isinstance(interaction, discord.message.Message):
                await interaction.channel.send(f">>> **Error：{e}**")
            logger.error(f"Error：{e}")

class Event(Cog_Extension):
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        if self.bot.user in message.mentions:
            if not MENTION_CHANNEL_ID or message.channel.id == MENTION_CHANNEL_ID:
                content = re.sub(r'<@.*?>', '', message.content).strip()
                client = get_client()
                conversation_style_str = client.get_conversation_style()
                chatbot = client.get_chatbot()
                if len(content) > 0:
                    username = str(message.author)
                    channel = str(message.channel)
                    if message.attachments:
                        for attachment in message.attachments:
                            if "image" in attachment.content_type:
                                logger.info(f"\x1b[31m{username}\x1b[0m：'{content}' ({channel}) [Style: {conversation_style_str}]")
                                async with message.channel.typing():
                                    await send_message(message, chatbot, conversation_style_str, content, attachment.url)
                            else:
                                await message.channel.send("> **ERROE：This file format is not supported.**")
                    else:
                        logger.info(f"\x1b[31m{username}\x1b[0m：'{content}' ({channel}) [Style: {conversation_style_str}]")
                        async with message.channel.typing():
                            await send_message(message, chatbot, conversation_style_str, content)
                else:
                    await message.channel.send(view=DropdownView())
            elif MENTION_CHANNEL_ID is not None:
                await message.channel.send(f"> **Can only be mentioned at <#{MENTION_CHANNEL_ID}>**")
        else:
            try:
                if isinstance(message.channel, discord.Thread):
                    users_chatbot = get_users_chatbot()
                    user_id = message.author.id
                    
                    if user_id not in users_chatbot:
                        return
                    
                    user_thread = users_chatbot[user_id].get_thread()
                    username = str(message.author)
                    channel = str(message.channel)

                    if user_thread != None and user_thread.id == message.channel.id:
                        content = message.content
                        logger.info(f"\x1b[31m{username}\x1b[0m：'{content}' ({channel}) [Style: {users_chatbot[user_id].get_conversation_style()}]")
                        if message.attachments:
                            for attachment in message.attachments:
                                if "image" in attachment.content_type:
                                    await users_chatbot[user_id].send_message(message=content, image=attachment.url)
                                else:
                                    await message.channel.send("> **ERROE：This file format is not supported.**")
                        else:
                            await users_chatbot[user_id].send_message(message=content)
            except Exception as e:
                await message.channel.send(f"> **ERROR：{e}**")
                logger.error(f"Error：{e}")   
                    
                        
async def setup(bot):
    await bot.add_cog(Event(bot))