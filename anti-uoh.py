import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.reactions = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

ROLE_MESSAGE_ID = 1516025346800222313

ROLE_MAP = {
    "♀️": "body type 2",
    "♂️": "body type 1",
    "🎨": "art",
    "📷": "irl pics",
    "🌸": "anime",
    "🎵": "music",
    "🟩": "wordle",
    "✨": "lumina",
    "🦉": "owo"
}

ALLOWED_ROLE_EMOJIS = set(ROLE_MAP.keys())

# 🚫 blocked emojis anywhere
BLOCKED_UNICODE = {"😭", "😢"}
BLOCKED_CUSTOM = {"bos"} 
SOBBER_ROLE_NAME = "sobber"

@bot.event
async def on_raw_reaction_add(payload):

    guild = bot.get_guild(payload.guild_id)
    if guild is None:
        return

    emoji = payload.emoji.name 
    
    member = await guild.fetch_member(payload.user_id)
    
    sobber_role = discord.utils.get(guild.roles, name=SOBBER_ROLE_NAME)
    is_sobber = sobber_role in member.roles if sobber_role else False
    
    
    if emoji in BLOCKED_UNICODE or emoji in BLOCKED_CUSTOM:
        
        if is_sobber:
            return
        
        channel = bot.get_channel(payload.channel_id)
        if channel:
            message = await channel.fetch_message(payload.message_id)
            member = await guild.fetch_member(payload.user_id)
            await message.remove_reaction(payload.emoji, member)
        return

    
    if payload.message_id != ROLE_MESSAGE_ID:
        return

    if emoji not in ALLOWED_ROLE_EMOJIS:
        return

    role = discord.utils.get(guild.roles, name=ROLE_MAP[emoji])
    if role:
        await member.add_roles(role)


@bot.event
async def on_raw_reaction_remove(payload):

    if payload.message_id != ROLE_MESSAGE_ID:
        return

    guild = bot.get_guild(payload.guild_id)
    member = await guild.fetch_member(payload.user_id)

    emoji = payload.emoji.name

    if emoji not in ROLE_MAP:
        return

    role = discord.utils.get(guild.roles, name=ROLE_MAP[emoji])
    if role:
        await member.remove_roles(role)


bot.run("da bot token u get from the dev portal website")
