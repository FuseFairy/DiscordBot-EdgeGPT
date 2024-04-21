import discord
import os
from dotenv import load_dotenv

load_dotenv()

async def check_channel(interaction: discord.Interaction, channel):
    allowed_channel_ids = os.getenv(channel, "").split(",")
    if str(interaction.channel.id) not in allowed_channel_ids and allowed_channel_ids[0] != "":
        allowed_channels_mention = ", ".join(f"<#{id_}>" for id_ in allowed_channel_ids)
        await interaction.followup.send(f"> **Command can only be used on: {allowed_channels_mention}**")
        return False
    return True