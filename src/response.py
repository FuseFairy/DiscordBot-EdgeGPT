import discord
import asyncio
from discord.ext import commands
from EdgeGPT import Chatbot, ConversationStyle
from src import log
from config import load_config 

bot = commands.Bot(command_prefix='!', intents = discord.Intents.all())
logger = log.setup_logger(__name__)
sem = asyncio.Semaphore(1)

# to add suggest responses
class MyView(discord.ui.View):
    def __init__(self, chatbot: Chatbot, conversation_style:str):
        super().__init__()
        for label in suggest_responses:
            button = discord.ui.Button(label=label)
            # button event
            async def callback(interaction: discord.Interaction):
                await interaction.response.defer(ephemeral=False, thinking=True)
                # when click the button, all buttons will disable.
                for child in self.children:
                    child.disabled = True
                await interaction.followup.edit_message(message_id=interaction.message.id, view=self)
                username = str(interaction.user)
                usermessage = button.label
                channel = str(interaction.channel)
                logger.info(f"\x1b[31m{username}\x1b[0m : '{usermessage}' ({channel}) [Style: {conversation_style}] [button]")
                task = asyncio.create_task(send_message(chatbot, interaction, usermessage, conversation_style))
                await asyncio.gather(task)
                self.stop()
            self.add_item(button)
            self.children[-1].callback = callback
    
async def send_message(chatbot: Chatbot, message: discord.Interaction, user_message: str, conversation_style: str):
    async with sem:
        try:
            ask = f"> **{user_message}** - <@{str(message.user.id)}> (***style: {conversation_style}***)\n\n"
            if conversation_style == "creative":
                reply = await chatbot.ask(prompt=user_message, conversation_style=ConversationStyle.creative)
            elif conversation_style == "precise":
                reply = await chatbot.ask(prompt=user_message, conversation_style=ConversationStyle.precise)
            else:
                reply = await chatbot.ask(prompt=user_message, conversation_style=ConversationStyle.balanced)
            try:
                text = reply["item"]["messages"][1]["text"]
            except:
                text = reply["item"]["messages"][1]["adaptiveCards"][0]["body"][0]["text"]
            # maybe no url
            if len(reply['item']['messages'][1]['sourceAttributions']) != 0:
                i = 1
                all_url = ""
                for url in reply['item']['messages'][1]['sourceAttributions']:
                    text = str(text).replace(f"[^{i}^]", "")
                    all_url += f"{url['providerDisplayName']}\n-> [{url['seeMoreUrl']}]\n\n"
                    i+=1
                response = f"{ask}```{all_url}```\n{text}"
            else:
                response = f"{ask}{text}"
            # discord characters limit 
            while len(response) > 2000:
                temp = response[:2000]
                response = response[2000:]
                await message.followup.send(temp)
            if load_config.config["USE_SUGGEST_RESPONSES"]:
                global suggest_responses
                suggest_responses = []
                try:
                    # add all suggest in list
                    for suggest in reply["item"]["messages"][1]["suggestedResponses"]:
                        suggest_responses.append(suggest["text"])
                    await message.followup.send(response, view=MyView(chatbot, conversation_style))
                except:
                    await message.followup.send(response)
            else:
                await message.followup.send(response)
        except Exception as e:
            if reply["item"]["result"]["value"] == "Throttled":
                await message.followup.send("> **Error: We're sorry, but you've reached the maximum number of messages you can send to Bing in a 24-hour period. Check back later!**")
                logger.exception(f"Error while sending message: {reply['item']['result']['error']}")
            else:
                await message.followup.send("> **Error: Something went wrong, please try again later or reset Bing!**")
                logger.exception(f"Error while sending message: {e}")