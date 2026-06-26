import aiohttp
import random
import threading
import asyncio
from flask import Flask, request
from datetime import datetime, timedelta
import discord
from discord.ext import commands
from discord.ext import tasks

intents = discord.Intents.default()
intents.reactions = True
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

ROLE_MESSAGE_ID = 1516025346800222313
WORDLE_ROLE_ID = 1516035868920512653
WORDLE_CHANNEL_ID = 1495729186537734155

CHANNELS = {
    "quanuy":1340058523509198901,
    "cult":1495728410515734720,
    "wordle":1495729186537734155,
    "testing":1518996249322324049,
    "aimran":1440053973058064461
}

GIPHY_API_KEY = "the giphy api key xd, since tenor doesnt allow it anymore"
KLIPY_API_KEY = "klipy's api key, both of these have a limit of 100 gifs per hour"

WEB_HISTORY = []

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

    if now.hour == 0 and now.minute == 0 and now.second == 0:
        channel = bot.get_channel(WORDLE_CHANNEL_ID)
        role = channel.guild.get_role(WORDLE_ROLE_ID)

        await channel.send(f"{role.mention} Daily Wordle time! 🟩")
    
    elif now.hour == 23 and now.minute >=50 and now.second == 0:
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


# help
@bot.command(aliases=["h"])
async def help(ctx):

    embed = discord.Embed(
        title="Spaghetti Bot Help 🐰",
        description="Commands you can use:",
        color=discord.Color.pink()
    )

    embed.add_field(
        name="`!bnuy`",
        value="Sends a random bunny gif 🐰",
        inline=False
    )

    embed.add_field(
        name="`!wordle`",
        value="Shows time remaining until the next Wordle 🟩",
        inline=False
    )

    embed.add_field(
        name="`!! + query` or `oi + query`",
        value="Searches GIPHY for a random gif.\nExample: `!!anime` or `oininjago`",
        inline=False
    )

    embed.add_field(
        name="`?? + query` or `oo + query`",
        value="Searches KLIPY for a random gif.\nExample: `??quaso` or `oobnuy`",
        inline=False
    )
    
    embed.add_field(
        name="also",
        value="also removes the :sob: from message reactions unless u ask nicely for the role:3",
        inline=False
    )
    
    embed.set_footer(text="yeah")

    await ctx.send(embed=embed)

# messager
app = Flask(__name__)

@app.route("/")
def home():
    return '''
    <style>
        body {
            background: #2b2d31;
            color: white;
            font-family: Arial;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }

        .box {
            background: #313338;
            width: 700px;
            padding: 20px;
            border-radius: 20px;
        }

        #history {
            background: #1e1f22;
            height: 400px;
            overflow-y: scroll;
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 10px;
        }

        textarea {
            width: 100%;
            height: 70px;
            border-radius: 10px;
        }

        button {
            margin-top: 10px;
            width: 100%;
            height: 40px;
        }
    </style>

    <div class="box">
        <h1>Spaghetti Messenger 🐰</h1>

        <select id="channel">
        <option value="quanuy">quanuy</option>
        <option value="cult">cult</option>
        <option value="wordle">wordle</option>
        <option value="testing">testing</option>
        <option value="aimran">aimran</option>
        </select>

        <br><br>
        
        <div id="history"></div>

        <textarea id="msg"></textarea>

        <button onclick="send()">Send</button>
    </div>

    <script>
        async function send() {
            let text = document.getElementById("msg").value;
            let channel = document.getElementById("channel").value;
            
            if(text.trim() === "") return;
            
            await fetch("/send", {
                method: "POST",
                headers: {
                    "Content-Type":"application/json"
                },
                body: JSON.stringify({
                    message:text,
                    channel:channel
                })
            });

            document.getElementById("msg").value = "";
            
            loadHistory();
        }
        
        async function loadHistory(){

        let response =
            await fetch("/history");

        let data = await response.json();

        let history =
            document.getElementById("history");

        history.innerHTML = "";

        data.messages.forEach(msg => {
            history.innerHTML += msg + "<br>";
        });

        history.scrollTop = history.scrollHeight;
        }

        setInterval(loadHistory, 1000);

        document.getElementById("msg")
            .addEventListener("keydown", e => {
                if(e.key==="Enter" && !e.shiftKey){
                    e.preventDefault();
                    send();
                }
            });
    </script>
    '''

@app.route("/send", methods=["POST"])
def send_message():
    data = request.json
    text = data["message"]
    channel_name = data["channel"]
    channel = bot.get_channel(CHANNELS[channel_name])
    
    if channel is None:
        return {"status": "error"}
    
    WEB_HISTORY.append(f"-> [{channel_name}] {text}")
    
    asyncio.run_coroutine_threadsafe(
        channel.send(text),
        bot.loop
    )
    
    return {"status": "ok"}

@app.route("/history")
def history():
    return{"messages": WEB_HISTORY}

def run_flask():
    app.run(host="127.0.0.1", port=5000)

threading.Thread(target=run_flask, daemon=True).start()


bot.run("da bot token u get from the discord dev portal website")
