import aiohttp
import random
from datetime import datetime, timedelta
import discord
from discord.ext import commands
from discord.ext import tasks

intents = discord.Intents.default()
intents.reactions = True
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# u get these from discord:
ROLE_MESSAGE_ID = 1516025346800222313
WORDLE_ROLE_ID = 1516035868920512653
WORDLE_CHANNEL_ID = 1495729186537734155

GIPHY_API_KEY = "the giphy api key xd, since tenor doesnt allow it anymore"
KLIPY_API_KEY = "klipy's api key, both of these have a limit of 100 gifs per hour"


ROLE_MAP = {
    "♀️": "body type 2",
    "♂️": "body type 1",
    "🎨": "art",
    "📷": "irl pics",
    "🌸": "cinema",
    "🎵": "music",
    "🟩": "wordle",
    "✨": "lumina",
    "🦉": "owo"
}

ALLOWED_ROLE_EMOJIS = set(ROLE_MAP.keys())


BLOCKED_UNICODE = {"😭", "😢"}
BLOCKED_CUSTOM = {"bos", "pinksob", "clownsob", "aliensob"} 
SOBBER_ROLE_NAME = "sobber"

# removes the blocked reactions and assigns role
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

# revokes role
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

# !bnuy for random bunny gif
@bot.command()
async def bnuy(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.bunnies.io/v2/loop/random/?media=gif,png") as resp:
            data = await resp.json()

            url = data["media"]["gif"]  # or "poster" for a static image

            embed = discord.Embed(title="buni >w< 🐰")
            embed.set_image(url=url)

            await ctx.send(embed=embed)

# wordle reminder at (my) midnight
@tasks.loop(seconds=1)
async def wordle_reminder():
    now = datetime.now()

    if now.hour == 0 and now.minute == 0:
        channel = bot.get_channel(WORDLE_CHANNEL_ID)
        role = channel.guild.get_role(WORDLE_ROLE_ID)

        await channel.send(f"{role.mention} Daily Wordle time! 🟩")
    
    elif now.hour == 23 and now.minute >=50:
        channel = bot.get_channel(WORDLE_CHANNEL_ID)
        minutes_left = 60 - now.minute
        
        await channel.send(minutes_left)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    if not wordle_reminder.is_running():
        wordle_reminder.start()


# checks time until midnight (in minutes)
@bot.command()
async def wordle(ctx):
    now = datetime.now()

    tomorrow = (now + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    remaining = tomorrow - now
    minutes = int(remaining.total_seconds() // 60)

    await ctx.send(
        f"Next Wordle in **{minutes} minutes**! 🟩"
    )

# random gif
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.startswith("oi") or message.content.startswith("!!"):
        query = message.content[2:].strip()

        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.giphy.com/v1/gifs/search",
                params={
                    "api_key": GIPHY_API_KEY,
                    "q": query,
                    "limit": 10,
                    "rating": "g"
                }
            ) as resp:
                data = await resp.json()

                if data["data"]:
                    gif = random.choice(data["data"])
                    await message.channel.send(
                        gif["images"]["original"]["url"]
                    )
                else:
                    await message.channel.send("no gif hehe https://tenor.com/view/raiden-shogun-middle-finger-raiden-ei-genshin-impact-hoyoverse-gif-1704467523727458703")

    elif message.content.startswith("??") or message.content.startswith("oo"):
        query = message.content[2:].strip()
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.klipy.com/v2/search",
                params={
                    "q": query,
                    "key": KLIPY_API_KEY,
                    "limit": 10
                }
            ) as resp:

                data = await resp.json()

                if data.get("results"):
                    gif = random.choice(data["results"])

                    gif_url = gif["media_formats"]["gif"]["url"]

                    await message.channel.send(gif_url)
                else:
                    await message.channel.send("gif not found https://tenor.com/view/raiden-shogun-middle-finger-raiden-ei-genshin-impact-hoyoverse-gif-1704467523727458703")


    await bot.process_commands(message)
 
bot.run("da bot token u get from the discord dev portal website")
