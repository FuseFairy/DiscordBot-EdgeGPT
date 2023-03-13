import discord
import asyncio
from EdgeGPT import Chatbot
from discord.ext import commands
from core.classes import Cog_Extension
from src import log
from dotenv import load_dotenv

load_dotenv()

bot = commands.Bot(command_prefix='!', intents = discord.Intents.all())
chatbot = Chatbot("./cookies.json")

logger = log.setup_logger(__name__)

sem = asyncio.Semaphore(1)

async def send_message(message, user_message):
    async with sem:
        try:
            ask = f"> **{user_message}** - <@{str(message.user.id)}> \n\n"
            temp = await chatbot.ask(user_message)
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

class edgegpt(Cog_Extension):
    @bot.tree.command(name = "bing", description = "Have a chat with Bing")
    async def bing(self, interaction: discord.Interaction, *, message: str):
        if interaction.user == bot.user:
            return
        await interaction.response.defer(ephemeral=False, thinking=True)
        username = str(interaction.user)
        usermessage = message
        channel = str(interaction.channel)
        logger.info(f"\x1b[31m{username}\x1b[0m : '{usermessage}' ({channel}) [EdgeGPT]")
        task = asyncio.create_task(send_message(interaction, usermessage))
        await asyncio.gather(task)

    @bot.tree.command(name="reset_bing", description="Complete reset Bing conversation history")
    async def resetbing(self, interaction: discord.Interaction):
        open('discord_bot.log', 'w').close()
        await interaction.response.defer(ephemeral=False)
        await chatbot.reset()
        await interaction.followup.send("> **Info: Reset finish.**")
        logger.warning("\x1b[31mBing has been successfully reset\x1b[0m")

async def setup(bot):
    await bot.add_cog(edgegpt(bot))