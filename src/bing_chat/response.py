import discord
import re
from re_edge_gpt import Chatbot
from re_edge_gpt import ConversationStyle
from src import log
from src.bing_chat.button_view import ButtonView

logger = log.setup_logger(__name__)

async def send_message(chatbot: Chatbot, user_message: str, image: str, conversation_style_str: str, users_chatbot=None, user_id=None, thread: discord.threads.Thread=None, interaction: discord.Interaction=None):
    reply = ''
    text = ''
    link_embed = ''
    all_url = []
    
    if interaction:
        if not interaction.response.is_done():
            await interaction.response.defer(thinking=True)
    else:
        await thread.typing()

    try:
        # Change conversation style
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
        text = f"{reply['text']}"
        text = re.sub(r'\[\^(\d+)\^\]', lambda match: '', text)
        
        # Get the URL, if available
        urls = re.findall(r'\[(\d+)\. (.*?)\]\((https?://.*?)\)', reply["sources_link"])
        if len(urls) > 0:
            for url in urls:
                all_url.append(f"{url[0]}. [{url[1]}]({url[2]})")
            link_text = "\n".join(all_url)
            link_embed = discord.Embed(description=link_text)
        
        # Set the final message
        user_message = user_message.replace("\n", "")
        # ask = f"> **{user_message}** - <@{str(interaction.user.id)}> (***style: {conversation_style_str}***)\n\n"
        response = f"{text} \n(***style: {conversation_style_str}***)"
        
        # Discord limit about 2000 characters for a message
        while len(response) > 2000:
            temp = response[:2000]
            response = response[2000:]
            await interaction.followup.send(temp)
            
        suggest_responses = reply["suggestions"]
        if interaction:
            if link_embed:
                await interaction.followup.send(response, view=ButtonView(conversation_style_str, suggest_responses, users_chatbot, user_id), embed=link_embed)
            else:
                await interaction.followup.send(response, view=ButtonView(conversation_style_str, suggest_responses, users_chatbot, user_id))
        else:
            if link_embed:
                await thread.send(content=response, view=ButtonView(conversation_style_str, suggest_responses, users_chatbot, user_id), embed=link_embed)
            else:
                await thread.send(content=response, view=ButtonView(conversation_style_str, suggest_responses, users_chatbot, user_id))

    except Exception as e:
        await interaction.followup.send(f"> **ERROR: {e}**")