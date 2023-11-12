import discord
import asyncio
from re_edge_gpt import ImageGen, ImageGenAsync
from src import log

logger = log.setup_logger(__name__)

async def create_image(interaction: discord.Interaction, prompt: str, auth_cookie: str):
    try:
        embeds = []
        username = interaction.user
        channel = interaction.channel
        prompts = f"> **{prompt}** - <@{str(interaction.user.id)}> (***BingImageCreator***)\n\n"
        
        logger.info(f"{username}: {prompt} ({channel}) [BingImageCreator]")

        # Fetches image links 
        async_gen = ImageGenAsync(auth_cookie=auth_cookie, quiet=True)
        images = await async_gen.get_images(prompt=prompt)
        
        # Add embed to list of embeds
        [embeds.append(discord.Embed(url="https://www.bing.com/").set_image(url=image_link)) for image_link in images]
        await interaction.followup.send(prompts, embeds=embeds, wait=True)
    except asyncio.TimeoutError:
        await interaction.followup.send("> **Error: Request timed out.**")
        logger.error("Error while create image: Request timed out.")
    except Exception as e:
        await interaction.followup.send(f"> **Error: {e}**")
        logger.error(f"Error while create image: {e}")