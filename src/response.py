import discord
import asyncio
from EdgeGPT import Chatbot, ConversationStyle
from src import log
from dotenv import load_dotenv

load_dotenv()

logger = log.setup_logger(__name__)
sem = asyncio.Semaphore(1)

async def send_message(chatbot: Chatbot, message: discord.Integration, user_message: str, conversation_style: str):
    async with sem:
        try:
            ask = f"> **{user_message}** - <@{str(message.user.id)}> \n\n"
            if conversation_style == "creative":
                temp = await chatbot.ask(prompt=user_message, conversation_style=ConversationStyle.creative)
            elif conversation_style == "precise":
                temp = await chatbot.ask(prompt=user_message, conversation_style=ConversationStyle.precise)
            else:
                temp = await chatbot.ask(prompt=user_message, conversation_style=ConversationStyle.balanced)
            try:
                text = temp["item"]["messages"][1]["text"]
            except:
                text = temp['item']['messages'][1]['adaptiveCards'][0]['body'][0]['text']
                
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
            await message.followup.send(response)
        except Exception as e:
            await message.followup.send("> **Error: Something went wrong, please try again later!**")
            logger.exception(f"Error while sending message: {e}")