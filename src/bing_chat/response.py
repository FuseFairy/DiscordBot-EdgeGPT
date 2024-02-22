import discord
import re
from re_edge_gpt import ConversationStyle
from ..log import setup_logger
from contextlib import aclosing
from .jail_break import sydney, config
from .button_view import ButtonView

logger = setup_logger(__name__)

config = config.Config()

async def send_message(chatbot, user_message: str, image: str, conversation_style_str: str, jailbreak: bool, chat_history: str, users_chatbot=None, user_id=None, thread: discord.threads.Thread=None, interaction: discord.Interaction=None):
    reply = ''
    text = ''
    link_embed = ''
    all_url = []
    urls = []
    suggest_responses = []
    
    if interaction:
        if not interaction.response.is_done():
            await interaction.response.defer(thinking=True)

    try:        
        if jailbreak:
            async with aclosing(sydney.ask_stream(
                conversation=chatbot,
                prompt=user_message,
                context=chat_history,
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
                users_chatbot[user_id].update_chat_history(f"\n\n[user](#message) \n{user_message} \n\n[assistant](#message) \n{text}")
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
            text = text[:end]
            text = re.sub(r'\[\^(\d+)\^\]',  '', text)
            text = re.sub(r'<[^>]*>', '', text)
            matches = re.findall(r'- \[.*?\]', text)
            for match in matches:
                content_within_brackets = match[:2] + match[3:-1]  # Remove brackets
                text = text.replace(match, content_within_brackets)
            text = re.sub(r'\(\^.*?\^\)', '', text)
            
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
            if link_embed:
                await interaction.followup.send(response, view=ButtonView(conversation_style_str, suggest_responses, users_chatbot, user_id), embed=link_embed)
            else:
                await interaction.followup.send(response, view=ButtonView(conversation_style_str, suggest_responses, users_chatbot, user_id))
        elif suggest_responses:
            if link_embed:
                await thread.send(content=response, view=ButtonView(conversation_style_str, suggest_responses, users_chatbot, user_id), embed=link_embed)
            else:
                await thread.send(content=response, view=ButtonView(conversation_style_str, suggest_responses, users_chatbot, user_id))
        elif interaction:
            if link_embed:
                await interaction.followup.send(response, embed=link_embed)
            else:
                await interaction.followup.send(response)
        else:
            if link_embed:
                await thread.send(content=response, embed=link_embed)
            else:
                await thread.send(content=response)

    except Exception as e:
        if interaction:
            await interaction.followup.send(f"> **ERROR: {e}**")
        else:
            await thread.send(f"> **ERROR: {e}**")