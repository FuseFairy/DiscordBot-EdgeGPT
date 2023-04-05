import discord
import json
import os
import asyncio
import aiohttp
from BingImageCreator import ImageGenAsync
from src import log

with open("./cookies.json", encoding="utf-8") as file:
    cookie_json = json.load(file)
    for cookie in cookie_json:
        if cookie.get("name") == "_U":
            auth_cookie = cookie.get("value")
            break

image_generator = ImageGenAsync(auth_cookie, True)
logger = log.setup_logger(__name__)
sem = asyncio.Semaphore(1)
try:
    os.mkdir("images")
except:
    pass

async def create_image(interaction: discord.Interaction, prompt: str):
    async with sem:
        try:
            files = []
            # Delete image from file
            [os.remove(f"./images/{image}") for image in os.listdir("./images")]
            prompts = f"> **{prompt}** - <@{str(interaction.user.id)}> (***BingImageCreator***)\n\n"
            # Fetches image links
            image_link = await image_generator.get_images(prompt)
            # Download imageawait asyncio.sleep(10)
            async with aiohttp.ClientSession() as session:
                for i, link in enumerate(image_link):
                    async with session.get(link) as response:
                        content = await response.read()
                        with open(os.path.join("./images", f"{i}.jpeg"), "wb") as f:
                            f.write(content)
            # Add image to list
            [files.append(discord.File(f"./images/{image}")) for image in os.listdir("./images")]
            await interaction.followup.send(prompts, files=files)
            await asyncio.sleep(15)
        except Exception as e:
            await interaction.followup.send(f"> **{e}**")
            logger.exception(f"Error while create image: {e}")
            await asyncio.sleep(15)
