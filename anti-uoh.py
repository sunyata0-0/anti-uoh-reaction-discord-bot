import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.reactions = True
intents.guilds = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_raw_reaction_add(payload):
    if payload.emoji.name != "😭":
        return

    channel = bot.get_channel(payload.channel_id)
    if not channel:
        return

    message = await channel.fetch_message(payload.message_id)

    member = await channel.guild.fetch_member(payload.user_id)

    await message.remove_reaction(payload.emoji, member)

bot.run("da bot token u get from the dev portal website")