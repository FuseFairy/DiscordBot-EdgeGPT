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
            response = '> **' + user_message + '** - <@' + \
                str(message.user.id) + '> \n\n'
            response = f"{response}{(await chatbot.ask(user_message))['item']['messages'][1]['adaptiveCards'][0]['body'][0]['text']}"
            if len(response) > 1900:
                # Split the response into smaller chunks of no more than 1900 characters each(Discord limit is 2000 per chunk)
                if "```" in response:
                    # Split the response if the code block exists
                    parts = response.split("```")
                    # Send the first message
                    await message.followup.send(parts[0])
                    # Send the code block in a seperate message
                    code_block = parts[1].split("\n")
                    formatted_code_block = ""
                    for line in code_block:
                        while len(line) > 1900:
                            # Split the line at the 50th character
                            formatted_code_block += line[:1900] + "\n"
                            line = line[1900:]
                        formatted_code_block += line + "\n"  # Add the line and seperate with new line

                    # Send the code block in a separate message
                    if (len(formatted_code_block) > 2000):
                        code_block_chunks = [formatted_code_block[i:i+1900]
                                            for i in range(0, len(formatted_code_block), 1900)]
                        for chunk in code_block_chunks:
                            await message.followup.send("```" + chunk + "```")
                    else:
                        await message.followup.send("```" + formatted_code_block + "```")

                    if len(parts) >= 3:
                        await message.followup.send(parts[2])
                else:
                    response_chunks = [response[i:i+1900]
                                    for i in range(0, len(response), 1900)]
                    for chunk in response_chunks:
                        await message.followup.send(chunk)
            else:
                await message.followup.send(response)
        except Exception as e:
            await message.followup.send("> **Error: Something went wrong, please try again later!**")
            logger.exception(f"Error while sending message: {e}")

class edgegpt(Cog_Extension):
    @bot.tree.command(name = "bing", description = "Have a chat with EdgeGPT")
    async def bing(self, interaction: discord.Interaction, *, message: str):
        if interaction.user == bot.user:
            return
        await interaction.response.defer(ephemeral=False,thinking=True)
        username = str(interaction.user)
        usermessage = message
        channel = str(interaction.channel)
        logger.info(f"\x1b[31m{username}\x1b[0m : '{usermessage}' ({channel}) [EdgeGPT]")
        task = asyncio.create_task(send_message(interaction, usermessage))
        await asyncio.gather(task)

    @bot.tree.command(name="reset", description="Reset Bing conversation history")
    async def reset(self, interaction: discord.Interaction):
        open('discord_bot.log', 'w').close()
        chatbot.reset()
        await interaction.response.defer(ephemeral=False)
        await interaction.followup.send("> **Info: Reset finish.**")
        logger.warning("\x1b[31mBing has been successfully reset\x1b[0m")

async def setup(bot):
    await bot.add_cog(edgegpt(bot))
