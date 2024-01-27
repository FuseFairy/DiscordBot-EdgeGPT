import discord
from core.classes import Cog_Extension
from discord import app_commands

class Help(Cog_Extension):
    @app_commands.command(name = "help", description = "Show how to use")
    async def help(self, interaction: discord.Interaction):
        embed=discord.Embed(description="[FuseFairy/DiscordBot-EdgeGPT](https://github.com/FuseFairy/DiscordBot-EdgeGPT/blob/main/README.md)\n***COMMANDS -***")
        embed.add_field(name="/cookies setting", value="Set and delete your Bing Cookies.", inline=False)
        embed.add_field(name="/copilot", value="Chat with Bing.", inline=False)
        embed.add_field(name="/reset conversation", value="Reset your Bing conversation.", inline=False)
        embed.add_field(name="/switch style", value="Switch your Bing conversation style.", inline=False)
        embed.add_field(name="/create image", value="Generate image by Bing Image Creator.", inline=False)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))