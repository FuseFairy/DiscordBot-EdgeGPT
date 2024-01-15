import discord

class ButtonView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, prompt: str, images: list, users_chatbot: dict, user_id: int):
        super().__init__(timeout=180)
        self.button_author = interaction.user.id
        self.prompt = prompt
        self.users_chatbot = users_chatbot
        self.user_id = user_id

        for i, image in enumerate(images, start=1):
            if i > 2:
                self.add_item(discord.ui.Button(label=f"Link {i}", url=image, row=2))
            else:
                self.add_item(discord.ui.Button(label=f"Link {i}", url=image, row=1))
            

    # Button event
    @discord.ui.button(label="Regenerate", emoji="🔂", row=3, style=discord.ButtonStyle.blurple)
    async def callback(self,interaction: discord.Interaction, button: discord.ui.Button):
        if  interaction.user.id != self.button_author:
            await interaction.response.defer(ephemeral=True, thinking=True)
            await interaction.followup.send("You don't have permission to press this button.")
        else:
            await interaction.response.defer(ephemeral=False, thinking=True)
            await self.users_chatbot[self.user_id].create_image(interaction, self.prompt)

