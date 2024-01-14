import discord
from src import log
from functools import partial

logger = log.setup_logger(__name__)

# To add suggest responses
class ButtonView(discord.ui.View):
    def __init__(self, conversation_style_str:str, suggest_responses:list, users_chatbot, user_id):
        super().__init__(timeout=120)

        # Add buttons
        for label in suggest_responses:
            button = discord.ui.Button(label=label)
            # Button event
            async def callback(interaction: discord.Interaction, button: discord.ui.Button):     
                await interaction.response.defer(ephemeral=False, thinking=True)
                username = str(interaction.user)
                usermessage = button.label
                channel = str(interaction.channel)
                logger.info(f"\x1b[31m{username}\x1b[0m : '{usermessage}' ({channel}) [Style: {conversation_style_str}] [button]")
                await users_chatbot[user_id].send_message(message=usermessage, interaction=interaction)
            self.add_item(button)
            self.children[-1].callback = partial(callback, button=button)