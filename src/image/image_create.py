import discord
import asyncio
import requests
from PIL import Image
from io import BytesIO
from re_edge_gpt import ImageGenAsync
from src import log
from src.image.button_view import ButtonView

logger = log.setup_logger(__name__)

async def create_image(interaction: discord.Interaction, users_chatbot: dict, prompt: str, auth_cookie: str):
    try:
        if not interaction.response.is_done():
            await interaction.response.defer(thinking=True)

        embeds = []
        user_id = interaction.user.id
        username = interaction.user
        channel = interaction.channel
        prompts = f"> **{prompt}** - <@{str(interaction.user.id)}> (***BingImageCreator***)\n\n"
        
        logger.info(f"\x1b[31m{username}\x1b[0m ： '{prompt}' ({channel}) [BingImageCreator]")

        # Fetches image links 
        async_gen = ImageGenAsync(auth_cookie=auth_cookie, quiet=True)
        images = await async_gen.get_images(prompt=prompt, timeout=300)
        images = [file for file in images if not file.endswith('.svg')]
        new_image = await concatenate_images(images)
        image_data = BytesIO()
        new_image.save(image_data, format='PNG')
        image_data.seek(0)
            
        # Add embed to list of embeds
        # [embeds.append(discord.Embed(url="https://www.bing.com/").set_image(url=image_link)) for image_link in images]
        await interaction.followup.send(prompts, file=discord.File(fp=image_data, filename='new_image.png'), view=ButtonView(interaction, prompt, images, users_chatbot, user_id))
    except asyncio.TimeoutError:
        await interaction.followup.send("> **Error: Request timed out.**")
        logger.error("Error while create image: Request timed out.")
    except Exception as e:
        await interaction.followup.send(f"> **Error: {e}**")
        logger.error(f"Error while create image: {e}")

async def concatenate_images(image_urls):
    images = [Image.open(BytesIO(requests.get(url).content)) for url in image_urls]

    if len(images) == 3 or len(images) == 4:
        new_image = Image.new('RGB', (1024*2, 1024*2))
    elif len(images) == 2:
        new_image = Image.new('RGB', (1024*2, 1024*1))
    else:
        new_image = Image.new('RGB', (1024*1, 1024*1))

    y_offset = 0
    x_offset = 0
    for image in images:
        if x_offset/image.width == 2:
            y_offset += image.height
            x_offset = 0

        new_image.paste(image, (x_offset, y_offset))
        
        x_offset += image.width

    return new_image