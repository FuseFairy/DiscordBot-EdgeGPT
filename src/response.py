import discord
import re
from EdgeGPT import Chatbot, ConversationStyle
from src import log
from config import load_config
from functools import partial

logger = log.setup_logger(__name__)
USE_SUGGEST_RESPONSES = load_config.config["USE_SUGGEST_RESPONSES"]
using_func = {}

# To add suggest responses
class MyView(discord.ui.View):
    def __init__(self,interaction: discord.Interaction, chatbot: Chatbot, conversation_style:str, suggest_responses:list):
        super().__init__(timeout=120)
        self.button_author =interaction.user.id
        # Add buttons
        for label in suggest_responses:
            button = discord.ui.Button(label=label)
            # Button event
            async def callback(interaction: discord.Interaction, button_author: int, button: discord.ui.Button):
                if interaction.user.id != button_author:
                    await interaction.response.defer(ephemeral=True, thinking=True)
                    await interaction.followup.send("You don't have permission to press this button.")
                elif not using_func[interaction.user.id]:
                    await interaction.response.defer(ephemeral=False, thinking=True)
                    # When click the button, all buttons will disable.
                    for child in self.children:
                        child.disabled = True
                    await interaction.followup.edit_message(message_id=interaction.message.id, view=self)
                    username = str(interaction.user)
                    usermessage = button.label
                    channel = str(interaction.channel)
                    logger.info(f"\x1b[31m{username}\x1b[0m : '{usermessage}' ({channel}) [Style: {conversation_style}] [button]")
                    await send_message(chatbot, interaction, usermessage, conversation_style)
                else:
                    await interaction.response.defer(ephemeral=True, thinking=True)
                    await interaction.followup.send("Please wait for your last conversation to finish.")
            self.add_item(button)
            self.children[-1].callback = partial(callback, button_author=self.button_author, button=button)

async def get_func_status(user_id):
    return using_func[user_id]

async def set_func_status(user_id, status: bool):
    using_func[user_id] = status

async def send_message(chatbot: Chatbot, interaction: discord.Interaction, user_message: str, conversation_style: str):
        using_func[interaction.user.id] = True
        superscript_map = {'0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'}
        reply = ''
        text = ''
        link_embed = ''
        images_embed = []
        all_url = []
        try:
            # Change conversation style
            if conversation_style == "creative":
                reply = await chatbot.ask(prompt=user_message, conversation_style=ConversationStyle.creative, wss_link="wss://sydney.bing.com/sydney/ChatHub")
            elif conversation_style == "precise":
                reply = await chatbot.ask(prompt=user_message, conversation_style=ConversationStyle.precise, wss_link="wss://sydney.bing.com/sydney/ChatHub")
            else:
                reply = await chatbot.ask(prompt=user_message, conversation_style=ConversationStyle.balanced, wss_link="wss://sydney.bing.com/sydney/ChatHub")
            # Get reply text
            try:
                text = f"{reply['item']['messages'][4]['text']}"
            except:
                text = f"{reply['item']['messages'][1]['text']}"
            text = re.sub(r'\[\^(\d+)\^\]', lambda match: ''.join(superscript_map.get(digit, digit) for digit in match.group(1)), text)
            # Get the URL, if available
            try:
                for search_results in reply["item"]["messages"][2]["groundingInfo"]:
                    for url in reply["item"]["messages"][2]["groundingInfo"][search_results]:
                        if url['title'] != None:
                            all_url.append(f"{url['index']}. [{url['title']}]({url['url']})")
                        else:
                            all_url.append(f"{url['index']}. [{url['url']}]({url['url']})")
                link_text = "\n".join(all_url)
                link_embed = discord.Embed(description=link_text)
            except:
                pass
            # Set the final message
            user_message = user_message.replace("\n", "")
            ask = f"> **{user_message}** - <@{str(interaction.user.id)}> (***style: {conversation_style}***)\n\n"
            response = f"{ask}{text}"
            # Discord limit about 2000 characters for a message
            while len(response) > 2000:
                temp = response[:2000]
                response = response[2000:]
                await interaction.followup.send(temp)
            # Get the image, if available
            try:
                all_image = re.findall("https?://[\w\./]+", str(reply["item"]["messages"][1]["adaptiveCards"][0]["body"][0]["text"]))
                [images_embed.append(discord.Embed(url="https://www.bing.com/").set_image(url=image_link)) for image_link in all_image]
            except:
                pass
            # Add all suggest responses in list
            if USE_SUGGEST_RESPONSES:
                suggest_responses = []
                try:
                    for suggest in reply["item"]["messages"]:
                        try:
                            for suggest_message in suggest["suggestedResponses"]:
                                suggest_responses.append(suggest_message["text"])
                        except:
                            pass
                except:
                    pass
                if images_embed:
                    await interaction.followup.send(response, view=MyView(interaction, chatbot, conversation_style, suggest_responses), embeds=images_embed, wait=True)                
                elif link_embed:
                    await interaction.followup.send(response, view=MyView(interaction, chatbot, conversation_style, suggest_responses), embed=link_embed, wait=True)
                else:
                    await interaction.followup.send(response, view=MyView(interaction, chatbot, conversation_style, suggest_responses), wait=True)
            else:
                if images_embed:
                    await interaction.followup.send(response, embeds=images_embed, wait=True)
                elif link_embed:
                    await interaction.followup.send(response, embed=link_embed, wait=True)
                else:
                    await interaction.followup.send(response, wait=True)
        except Exception as e:
                try:
                    if reply["item"]["throttling"]["numUserMessagesInConversation"] and reply["item"]["throttling"]["numUserMessagesInConversation"] > reply["item"]["throttling"]["maxNumUserMessagesInConversation"]:
                        await interaction.followup.send("> **Oops, I think we've reached the end of this conversation. Please reset the bot!**")
                        logger.exception(f"Error while sending message: The maximum number of conversations in a round has been reached")
                except:
                    await interaction.followup.send("> **Error: Please try again later or reset bot**")
                    logger.exception(f"Error while sending message: {e}")
        finally:
            using_func[interaction.user.id] = False