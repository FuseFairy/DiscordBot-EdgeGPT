import discord
import asyncio
from discord.ext import commands
from EdgeGPT import Chatbot, ConversationStyle
from src import log
from dotenv import load_dotenv
from config.load_config import config

load_dotenv()

bot = commands.Bot(command_prefix='!', intents = discord.Intents.all())
logger = log.setup_logger(__name__)
sem = asyncio.Semaphore(1)

# to add suggest responses
class MyView(discord.ui.View):
    def __init__(self, chatbot: Chatbot, conversation_style:str):
        super().__init__()
        for label in suggest_responses:
            button = discord.ui.Button(label=label)
            async def callback(interaction: discord.Interaction, button=button):
                username = str(interaction.user)
                usermessage = button.label
                channel = str(interaction.channel)
                logger.info(f"\x1b[31m{username}\x1b[0m : '{usermessage}' ({channel}) [Style: {conversation_style}] [button]")
                task = asyncio.create_task(send_message(chatbot, interaction, usermessage, conversation_style))
                await asyncio.gather(task)
            self.add_item(button)
            self.children[-1].callback = callback

async def send_message(chatbot: Chatbot, message: discord.Interaction, user_message: str, conversation_style: str):
    await message.response.defer(ephemeral=False, thinking=True)
    async with sem:
        global suggest_responses
        suggest_responses = []
        try:
            ask = f"> **{user_message}** - <@{str(message.user.id)}> \n\n"
            if conversation_style == "creative":
                temp = await chatbot.ask(prompt=user_message, conversation_style=ConversationStyle.creative)
            elif conversation_style == "precise":
                temp = await chatbot.ask(prompt=user_message, conversation_style=ConversationStyle.precise)
            else:
                temp = await chatbot.ask(prompt=user_message, conversation_style=ConversationStyle.balanced)
            # add all suggest in list
            try:
                for suggest in temp["item"]["messages"][1]["suggestedResponses"]:
                    suggest_responses.append(suggest["text"])
            except Exception as e:
                pass
            try:
                text = temp["item"]["messages"][1]["text"]
            except:
                text = temp["item"]["messages"][1]["adaptiveCards"][0]["body"][0]["text"]
            # maybe no url
            if len(temp['item']['messages'][1]['sourceAttributions']) != 0:
                i = 1
                all_url = ""
                for url in temp['item']['messages'][1]['sourceAttributions']:
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
            if config["USE_SUGGEST_RESPONSES"] and len(suggest_responses) != 0:
                await message.followup.send(response, view=MyView(chatbot, conversation_style))
            else:
                await message.followup.send(response)
        except Exception as e:
            await message.followup.send("> **Error: Something went wrong, please try again later!**")
            logger.exception(f"Error while sending message: {e}")