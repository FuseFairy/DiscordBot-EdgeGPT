import discord
from ..log import setup_logger
from functools import partial

logger = setup_logger(__name__)

# To add suggest responses
class ButtonView(discord.ui.View):
    def __init__(self, conversation_style_str:str=None, suggest_responses:list=None, user_chatbot=None, images:list=None):
        super().__init__(timeout=120)

        if images:
            for i, image in enumerate(images, start=1):
                if i > 2:
                    self.add_item(discord.ui.Button(label=f"Link {i}", url=image, row=2))
                else:
                    self.add_item(discord.ui.Button(label=f"Link {i}", url=image, row=1))

        if conversation_style_str and suggest_responses and user_chatbot:
            # Add buttons
            for label in suggest_responses:
                button = discord.ui.Button(label=label, row=3)
                # Button event
                async def callback(interaction: discord.Interaction, button: discord.ui.Button):     
                    await interaction.response.defer(ephemeral=False, thinking=True)
                    username = str(interaction.user)
                    usermessage = button.label
                    channel = str(interaction.channel)
                    logger.info(f"\x1b[31m{username}\x1b[0m ： '{usermessage}' ({channel}) [Style: {conversation_style_str}] [button]")
                    await user_chatbot.send_message(message=usermessage, interaction=interaction)
                self.add_item(button)
                self.children[-1].callback = partial(callback, button=button)