import discord
import os
from core.classes import Cog_Extension
from discord import app_commands
from src.check_channel import check_channel
from dotenv import load_dotenv

load_dotenv()

class Help(Cog_Extension):
    @app_commands.command(name = "help", description = "Show how to use")
    async def help(self, interaction: discord.Interaction):
        if not await check_channel(interaction, "HELP_CMD_CHANNEL_ID"):
            return

        embed=discord.Embed(description="[FuseFairy/DiscordBot-EdgeGPT](https://github.com/FuseFairy/DiscordBot-EdgeGPT/blob/main/README.md)\n***COMMANDS -***")
        embed.add_field(name="/cookies setting", value="Can upload own cookies.", inline=False)
        embed.add_field(name="/dalle3 setting", value="Can upload own api key, api key can get from https://dalle.feiyuyu.net/dashboard.", inline=False)
        embed.add_field(name="/copilot", value="Chat with Copilot or Sydney(jail break).", inline=False)
        embed.add_field(name="/reset conversation", value="Reset your conversation.", inline=False)
        embed.add_field(name="/create image", value="Generate image.", inline=False)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))