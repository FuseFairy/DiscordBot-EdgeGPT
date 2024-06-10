import discord
import asyncio
import requests
import aiohttp
import os
from PIL import Image
from io import BytesIO
from re_edge_gpt import ImageGenAsync
from src.log import setup_logger
from src.image.button_view import ButtonView
from dotenv import load_dotenv

load_dotenv()

logger = setup_logger(__name__)

async def create_image_dalle3(interaction: discord.Interaction, prompt: str, chatbot):
    try:
        username = interaction.user
        channel = interaction.channel
        api_key = chatbot.dalle3_unoffcial_apikey

        logger.info(f"\x1b[31m{username}\x1b[0m：'{prompt}' ({channel}) [Unofficial DALLE-3]")

        payload = {
            "prompt": prompt,
            "model": 'dall-e-3',
            "n": 1,
            "quality": 'standard',
            "response_format": 'url',
            "size": '1024x1024',
            "style": 'vivid',
            "user": 'free-dall-e-user'
        }

        headers = {"Authorization": "Bearer " + api_key}
        async with aiohttp.ClientSession() as session:
            current_task = asyncio.create_task(session.post("https://dalle.feiyuyu.net/v1/images/generations",proxy=os.getenv("PROXY"), json=payload, headers=headers))
            response = await current_task
            if response.status == 200:
                image_url = (await response.json())["data"][0]["url"]
                embed=discord.Embed(title="Unofficial DALLE-3", url="https://dalle.feiyuyu.net/gradio/", type="image")
                embed.add_field(name="prompt", value=f"{prompt}", inline=False)
                embed.set_image(url=image_url)
                embed.set_footer(text="Power by feiyuyu", icon_url="https://avatars.githubusercontent.com/u/32660959?v=4")
                await interaction.followup.send(embed=embed, view=ButtonView(interaction, prompt, chatbot))
            else:
                await interaction.followup.send(f"ERROR：{response.status} {response.reason}")
                logger.error(f"Error while create image：{response.status} {response.reason}")
    except Exception as e:
        await interaction.followup.send(f"> **Error：{e}**")
        logger.error(f"Error while create image：{e}")

async def create_image_bing(chatbot, interaction: discord.Interaction, prompt: str, cookies):
    try:
        if not interaction.response.is_done():
            await interaction.response.defer(thinking=True)

        user_id = interaction.user.id
        username = interaction.user
        channel = interaction.channel
        prompts = f"> **{prompt}** - <@{str(user_id)}> (***BingImageCreator***)\n\n"
        
        logger.info(f"\x1b[31m{username}\x1b[0m：'{prompt}' ({channel}) [BingImageCreator]")

        auth_cookie = ""
        for cookie in cookies:
            if cookie["name"] == "_U":
                auth_cookie =  cookie["value"]
                break

        async_gen = ImageGenAsync(auth_cookie=auth_cookie, quiet=True, proxy=os.getenv("PROXY"))
        images = await async_gen.get_images(prompt=prompt, timeout=int(os.getenv("IMAGE_TIMEOUT")), max_generate_time_sec=int(os.getenv("IMAGE_MAX_CREATE_SEC")))
        images = [file for file in images if not (file.endswith('.svg') or file.endswith('.js'))]
        new_image = await concatenate_images(images)
        image_data = BytesIO()
        new_image.save(image_data, format='PNG')
        image_data.seek(0)
            
        await interaction.followup.send(prompts, file=discord.File(fp=image_data, filename='new_image.png'), view=ButtonView(interaction, prompt, chatbot, images))
    except asyncio.TimeoutError:
        await interaction.followup.send("> **ERROR：Request timed out.**")
        logger.error("Error while create image：Request timed out.")
    except TypeError:
        await interaction.followup.send("> **ERROR：No images returned.**")
        logger.error("Error while create image：No images returned.")
    except Exception as e:
        await interaction.followup.send(f"> **ERROR：{e}**")
        logger.error(f"Error while create image：{e}")

async def concatenate_images(image_urls):
    images = [Image.open(BytesIO(requests.get(url).content)) for url in image_urls]

    if len(images) == 3 or len(images) == 4:
        new_image = Image.new('RGBA', (1024*2, 1024*2), (0, 0, 0, 0))
    elif len(images) == 2:
        new_image = Image.new('RGBA', (1024*2, 1024*1), (0, 0, 0, 0))
    else:
        new_image = Image.new('RGBA', (1024*1, 1024*1), (0, 0, 0, 0))

    y_offset = 0
    x_offset = 0
    for image in images:
        if x_offset/image.width == 2:
            y_offset += image.height
            x_offset = 0

        new_image.paste(image, (x_offset, y_offset))
        
        x_offset += image.width

    return new_image