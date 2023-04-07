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
            # Delete existing images
            [os.remove(f"./images/{image}") for image in os.listdir("./images")]
            prompts = f"> **{prompt}** - <@{str(interaction.user.id)}> (***BingImageCreator***)\n\n"
            # Fetches image links and download images
            await image_generator.save_images(await image_generator.get_images(prompt), "./images")
            # Add images to list of files
            [files.append(discord.File(f"./images/{image}")) for image in os.listdir("./images")]
            await interaction.followup.send(prompts, files=files, wait=True)
        except asyncio.TimeoutError:
            await interaction.followup.send("> **Error: Request timed out.**")
            logger.exception("Error while create image: Request timed out.")
        except Exception as e:
            await interaction.followup.send(f"> **Error: {e}**")
            logger.exception(f"Error while create image: {e}")
        finally:
            # Wait for 15 seconds before processing the next request
            await asyncio.sleep(15)
