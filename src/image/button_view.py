import discord

class ButtonView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, prompt: str, users_chatbot: dict, user_id: int):
        super().__init__(timeout=180)
        self.button_author = interaction.user.id
        self.prompt = prompt
        self.users_chatbot = users_chatbot
        self.user_id = user_id

    # Button event
    @discord.ui.button(label="Regenerate", emoji="🔂")
    async def callback(self,interaction: discord.Interaction, button: discord.ui.Button):
        if  interaction.user.id != self.button_author:
            await interaction.response.defer(ephemeral=True, thinking=True)
            await interaction.followup.send("You don't have permission to press this button.")
        else:
            await interaction.response.defer(ephemeral=False, thinking=True)
            await self.users_chatbot[self.user_id].create_image(interaction, self.prompt)

