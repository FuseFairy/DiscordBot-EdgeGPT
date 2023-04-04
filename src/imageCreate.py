import discord
import json
import os
import asyncio
from BingImageCreator import ImageGenAsync
from src import log

with open("./cookies.json", encoding="utf-8") as file:
    cookie_json = json.load(file)
    for cookie in cookie_json:
        if cookie.get("name") == "_U":
            auth_cookie = cookie.get("value")
            break

image_generator = ImageGenAsync(auth_cookie)
logger = log.setup_logger(__name__)
sem = asyncio.Semaphore(1)

async def create_image(interaction: discord.Interaction, prompt: str):
    async with sem:
        try:
            files = []
            prompts = f"> **{prompt}** - <@{str(interaction.user.id)}> (***BingImageCreator***)\n\n"
            # Fetches image links and download
            await image_generator.save_images(await image_generator.get_images(prompt), "./images")
            # Add image to list
            [files.append(discord.File(f"./images/{image}")) for image in os.listdir("./images")]
            await interaction.followup.send(prompts, files=files)
            # Delete image from file
            [os.remove(f"./images/{image}") for image in os.listdir("./images")]
        except Exception as e:
            await interaction.followup.send(f"> **{e}**")
            logger.exception(f"Error while create image: {e}")