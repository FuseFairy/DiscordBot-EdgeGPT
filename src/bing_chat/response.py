import discord
import re
import os
from io import BytesIO
from re_edge_gpt import ConversationStyle
from ..log import setup_logger
from contextlib import aclosing
from .jail_break import sydney, config
from .button_view import ButtonView
from re_edge_gpt import ImageGenAsync
from ..image.image_create import concatenate_images
from dotenv import load_dotenv

load_dotenv()

logger = setup_logger(__name__)

config = config.Config()

async def send_message(user_chatbot, user_message: str, image: str, interaction: discord.Interaction=None):
    reply = ''
    text = ''
    link_embed = ''
    all_url = []
    urls = []
    image_create_text = ""
    suggest_responses = []
    chatbot = user_chatbot.chatbot
    thread = user_chatbot.thread
    conversation_style_str = user_chatbot.conversation_style
    
    if interaction:
        if not interaction.response.is_done():
            await interaction.response.defer(thinking=True)

    try:        
        if user_chatbot.jailbreak:
            async with aclosing(sydney.ask_stream(
                conversation=chatbot,
                prompt=user_message,
                context=user_chatbot.chat_history,
                conversation_style=conversation_style_str,
                locale='en-US',
                wss_url='wss://' + config.get('wss_domain') + '/sydney/ChatHub',
                no_search=False
            )) as agen:
                async for response in agen:
                    if response["type"] == 2 and "item" in response and "messages" in response["item"]:
                        message = response["item"]["messages"]
                        text = ""
                        if "suggestedResponses" in message[-1]:
                            suggest_responses = list(map(lambda x: x["text"], message[-1]["suggestedResponses"]))
                            text = message[-1]["text"]
                        elif "suggestedResponses" in message[-2]:
                            suggest_responses = list(map(lambda x: x["text"], message[-2]["suggestedResponses"]))
                            text = message[-2]["text"]
                        if "sourceAttributions" in message[-1]:
                            urls = [(i+1, x["providerDisplayName"], x["seeMoreUrl"]) for i, x in  enumerate(message[-1]["sourceAttributions"]) if "providerDisplayName" in x and "seeMoreUrl" in x]
                            text = message[-1]["text"]
                        elif "sourceAttributions" in message[-2]:
                            urls = [(i+1, x["providerDisplayName"], x["seeMoreUrl"]) for i, x in  enumerate(message[-2]["sourceAttributions"]) if "providerDisplayName" in x and "seeMoreUrl" in x]
                            text = message[-2]["text"]
                        if text == "":
                            text = response['item']['result']['message']
                        break
                user_chatbot.chat_history += f"\n\n[user](#message) \n{user_message} \n\n[assistant](#message) \n{text}"
                text = re.sub(r'\[\^(\d+)\^\]',  '', text)
                text = re.sub(r':\s*\[[^\]]*\]\([^\)]*\)', '', text)
                text = re.sub(r'<[^>]*>', '', text)
        else:
            if conversation_style_str == "creative":
                conversation_style=ConversationStyle.creative
            elif conversation_style_str == "precise":
                conversation_style=ConversationStyle.precise
            else:
                conversation_style=ConversationStyle.balanced

            reply = await chatbot.ask(
                prompt=user_message,
                conversation_style=conversation_style,
                simplify_response=True,
                attachment={"image_url":f"{image}"}  
            )

            # Get reply text
            suggest_responses = reply["suggestions"]
            text = f"{reply['text']}"
            urls = [(i+1, x, reply["source_values"][i]) for i, x in  enumerate(reply["source_keys"])]
            end = text.find("Generating answers for you...")
            text = text[:end] if end != -1 else text
            end = text.find("Analyzing the image: Faces may be blurred to protect privacy.")
            text = text[:end] if end != -1 else text
            text = re.sub(r'\[\^(\d+)\^\]',  '', text)
            text = re.sub(r'<[^>]*>', '', text)
            matches = re.findall(r'- \[.*?\]', text)
            for match in matches:
                content_within_brackets = match[:2] + match[3:-1]
                text = text.replace(match, content_within_brackets)
            text = re.sub(r'\(\^.*?\^\)', '', text)
            
            # Generate image
            image_create_text = reply["image_create_text"]
            auth_cookie = ""
            if image_create_text:
                for cookie in user_chatbot.cookies:
                    if cookie["name"] == "_U":
                        auth_cookie =  cookie["value"]
                        break
                    
                async_gen = ImageGenAsync(auth_cookie=auth_cookie, quiet=True)
                images = await async_gen.get_images(prompt=image_create_text, timeout=int(os.getenv("IMAGE_TIMEOUT")), max_generate_time_sec=int(os.getenv("IMAGE_MAX_CREATE_SEC")))
                images = [file for file in images if not file.endswith('.svg')]
                new_image = await concatenate_images(images)
                image_data = BytesIO()
                new_image.save(image_data, format='PNG')
                image_data.seek(0)
            
        # Make URL Embed, if available
        if len(urls) > 0:
            for url in urls:
                if url[1]:
                    all_url.append(f"{url[0]}. [{url[1]}]({url[2]})")
                else:
                    all_url.append(f"{url[0]}. {url[2]}")
            link_text = "\n".join(all_url)
            link_embed = discord.Embed(description=link_text)
        
        # Set the final message
        text = text.strip()
        response = f"{text} \n(***style: {conversation_style_str}***)"

        # Discord limit about 2000 characters for a message
        while len(response) > 2000:
            temp = response[:2000]
            response = response[2000:]
            if interaction:
                await interaction.followup.send(temp)
            else:
                await thread.send(temp)
            
        if interaction and suggest_responses:
            if link_embed and image_create_text:
                await interaction.followup.send(response, file=discord.File(fp=image_data, filename='new_image.png'), view=ButtonView(conversation_style_str, suggest_responses, user_chatbot, images), embed=link_embed)
            elif link_embed:
                await interaction.followup.send(response, view=ButtonView(conversation_style_str, suggest_responses, user_chatbot), embed=link_embed)
            elif image_create_text:
                await interaction.followup.send(response, file=discord.File(fp=image_data, filename='new_image.png'), view=ButtonView(conversation_style_str, suggest_responses, user_chatbot, images))
            else:
                await interaction.followup.send(response, view=ButtonView(conversation_style_str, suggest_responses, user_chatbot))
        elif interaction:
            if link_embed and image_create_text:
                await interaction.followup.send(response, file=discord.File(fp=image_data, filename='new_image.png'), view=ButtonView(images), embed=link_embed)
            elif link_embed:
                await interaction.followup.send(response, embed=link_embed)
            elif image_create_text:
                await interaction.followup.send(response, file=discord.File(fp=image_data, filename='new_image.png'), view=ButtonView(images))
            else:
                await interaction.followup.send(response)
        elif suggest_responses:
            if link_embed and image_create_text:
                await thread.send(response, file=discord.File(fp=image_data, filename='new_image.png'), view=ButtonView(conversation_style_str, suggest_responses, user_chatbot, images), embed=link_embed)
            elif link_embed:
                await thread.send(response, view=ButtonView(conversation_style_str, suggest_responses, user_chatbot), embed=link_embed)
            elif image_create_text:
                await thread.send(response, file=discord.File(fp=image_data, filename='new_image.png'), view=ButtonView(conversation_style_str, suggest_responses, user_chatbot, images))
            else:
                await thread.send(response, view=ButtonView(conversation_style_str, suggest_responses, user_chatbot))
        else:
            if link_embed and image_create_text:
                await thread.send(response, file=discord.File(fp=image_data, filename='new_image.png'), view=ButtonView(images), embed=link_embed)
            elif link_embed:
                await thread.send(response, embed=link_embed)
            elif image_create_text:
                await thread.send(response, file=discord.File(fp=image_data, filename='new_image.png'), view=ButtonView(images))
            else:
                await thread.send(response)

    except Exception as e:
        if interaction:
            await interaction.followup.send(f"> **ERROR：{e}**")
        else:
            await thread.send(f"> **ERROR：{e}**")
        logger.error(e, exc_info=True)