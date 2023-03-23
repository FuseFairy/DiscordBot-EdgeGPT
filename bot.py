import discord
import os
import src.log
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv(dotenv_path="./.env")

bot = commands.Bot(command_prefix='!', intents = discord.Intents.all())

# init loggger
logger = src.log.setup_logger(__name__)

@bot.event
async def on_ready():
    logger.info(f'{bot.user} is now running!')
    for Filename in os.listdir('./cogs'):
        if Filename.endswith('.py'):
            await bot.load_extension(f'cogs.{Filename[:-3]}')  
    print("Bot is Up and Ready!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)
        
@bot.command()
async def load(ctx, extension):
    await bot.load_extension(f'cogs.{extension}')
    await ctx.send(f'Loaded {extension} done.')

@bot.command()
async def unload(ctx, extension):
    await bot.unload_extension(f'cogs.{extension}')
    await ctx.send(f'Un-Loaded {extension} done.')

@bot.command()
async def reload(ctx, extension):
    await bot.reload_extension(f'cogs.{extension}')
    await ctx.send(f'Re-Loaded {extension} done.')

@bot.command()
async def clean(ctx):
    open('discord_bot.log', 'w').close()
    await ctx.send(f'Has been emptied')

if __name__ == '__main__':
    bot.run(os.getenv("DISCORD_BOT_TOKEN"))