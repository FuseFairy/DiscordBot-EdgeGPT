import discord
import asyncio
from discord.ext import commands
from EdgeGPT import Chatbot, ConversationStyle
from src import log
from config import load_config
from functools import partial

bot = commands.Bot(command_prefix='!', intents = discord.Intents.all())
logger = log.setup_logger(__name__)
sem = asyncio.Semaphore(1)

# to add suggest responses
class MyView(discord.ui.View):
    def __init__(self, chatbot: Chatbot, conversation_style:str):
        super().__init__(timeout=120)
        for label in suggest_responses:
            button = discord.ui.Button(label=label)
            # button event
            async def callback(interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer(ephemeral=False, thinking=True)
                # when click the button, all buttons will disable.
                for child in self.children:
                    child.disabled = True
                await interaction.followup.edit_message(message_id=interaction.message.id, view=self)
                self.clear_items()
                username = str(interaction.user)
                usermessage = button.label
                channel = str(interaction.channel)
                logger.info(f"\x1b[31m{username}\x1b[0m : '{usermessage}' ({channel}) [Style: {conversation_style}] [button]")
                task = asyncio.create_task(send_message(chatbot, interaction, usermessage, conversation_style))
                await asyncio.gather(task)
        # add buttons to MyView()
        for label in suggest_responses:
            button = discord.ui.Button(label=label)
            self.add_item(button)
            self.children[-1].callback = partial(callback, button=button)

async def send_message(chatbot: Chatbot, message: discord.Interaction, user_message: str, conversation_style: str):
    async with sem:
        try:
            ask = f"> **{user_message}** - <@{str(message.user.id)}> (***style: {conversation_style}***)\n\n"
            # change conversation style
            if conversation_style == "creative":
                reply = await chatbot.ask(prompt=user_message, conversation_style=ConversationStyle.creative)
            elif conversation_style == "precise":
                reply = await chatbot.ask(prompt=user_message, conversation_style=ConversationStyle.precise)
            else:
                reply = await chatbot.ask(prompt=user_message, conversation_style=ConversationStyle.balanced)
            # get reply text
            text = reply["item"]["messages"][1]["text"]
            # Get the URL, if available
            embed = ''
            if len(reply['item']['messages'][1]['sourceAttributions']) != 0:
                i = 1
                all_url = []
                for url in reply['item']['messages'][1]['sourceAttributions']:
                    all_url.append(f"[{url['providerDisplayName']}]({url['seeMoreUrl']})")
                    i += 1
                link_text = "\n".join(all_url)
                embed = discord.Embed(title="Source Links", description=link_text)
            response = f"{ask}{text}"
            # discord limit about 2000 characters for a message
            while len(response) > 2000:
                temp = response[:2000]
                response = response[2000:]
                await message.followup.send(temp)
            # add all suggest responses in list
            if load_config.config["USE_SUGGEST_RESPONSES"]:
                global suggest_responses
                suggest_responses = []
                for suggest in reply["item"]["messages"][1]["suggestedResponses"]:
                    suggest_responses.append(suggest["text"])
                if embed:
                    await message.followup.send(response, view=MyView(chatbot, conversation_style), embeds=[embed])
                else:
                    await message.followup.send(response, view=MyView(chatbot, conversation_style))
            else:
                if embed:
                    await message.followup.send(response, embeds=[embed])
                else:
                    await message.followup.send(response)
        except:
            try:
                if reply["item"]["throttling"]["numUserMessagesInConversation"] > 15:
                    await message.followup.send("> **Oops, I think we've reached the end of this conversation. Please reset the bot, if you would!**")
                    logger.exception(f"Error while sending message: The maximum number of conversations in a round has been reached")
            except:    
                if reply["item"]["result"]["value"] == "Throttled":
                    await message.followup.send("> **Error: We're sorry, but you've reached the maximum number of messages you can send to Bing in a 24-hour period. Check back later!**")
                    logger.exception("Error while sending message: The daily conversation limit has been reached")
