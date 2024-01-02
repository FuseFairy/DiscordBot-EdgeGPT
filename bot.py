import discord
import os
import pkg_resources
import json
from discord.ext import commands
from dotenv import load_dotenv
from cogs.event import set_chatbot
from src.log import setup_logger

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents = intents)

# init loggger
logger = setup_logger(__name__)

def check_version():
    required = [line.strip() for line in open('requirements.txt')]

    for package in required:
        package_name, package_version = package.split('==')
        name, version = pkg_resources.get_distribution(package_name).project_name, pkg_resources.get_distribution(package_name).version
        if package != f'{name}=={version}':
            raise ValueError(f'{name} version {version} is installed but does not match the requirements')

@bot.event
async def on_ready():
    bot_status = discord.Status.online
    bot_activity = discord.Activity(type=discord.ActivityType.playing, name = "/help")
    await bot.change_presence(status = bot_status, activity = bot_activity)
    for Filename in os.listdir('./cogs'):
        if Filename.endswith('.py'):
            await bot.load_extension(f'cogs.{Filename[:-3]}')
    logger.info(f'{bot.user} is now running!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        logger.error(f"Error: {e}")

# Load command
@commands.is_owner()   
@bot.command()
async def load(ctx, extension):
    await bot.load_extension(f'cogs.{extension}')
    await ctx.author.send(f'> **Loaded {extension} done.**')

# Unload command
@commands.is_owner()
@bot.command()
async def unload(ctx, extension):
    await bot.unload_extension(f'cogs.{extension}')
    await ctx.author.send(f'> **Un-Loaded {extension} done.**')

# Empty discord_bot.log file
@commands.is_owner()
@bot.command()
async def clean(ctx):
    open('discord_bot.log', 'w').close()
    await ctx.author.send(f'> **Successfully emptied the file!**')

# Get discord_bot.log file
@commands.is_owner()
@bot.command()
async def getlog(ctx):
    try:
        with open('discord_bot.log', 'rb') as f:
            file = discord.File(f)
        await ctx.author.send(file=file)
        await ctx.author.send("> **Send successfully!**")
    except:
        await ctx.author.send("> **Send failed!**")

# Upload new Bing cookies and restart the bot
@commands.is_owner()
@bot.command()
async def upload(ctx):
    try:
        if ctx.message.attachments:
            for attachment in ctx.message.attachments:
                if str(attachment).find("message.txt"):
                    content = await attachment.read()
                    with open("cookies.json", "w", encoding = "utf-8") as f:
                        json.dump(json.loads(content), f, indent = 2)
                    if not isinstance(ctx.channel, discord.abc.PrivateChannel):
                        await ctx.message.delete()
                    await set_chatbot(json.loads(content))
                    await ctx.author.send(f'> **Upload new cookies successfully!**')
                    logger.info("\x1b[31mCookies has been setup successfully\x1b[0m")
                else:
                    await ctx.author.send("> **Didn't get any txt file.**")
        else:
            await ctx.author.send("> **Didn't get any file.**")
    except Exception as e:
        await ctx.author.send(f">>> **Error: {e}**")
        logger.exception(f"Error while upload cookies: {e}")

if __name__ == '__main__':
    check_version()
    bot.run(os.getenv("DISCORD_BOT_TOKEN"))