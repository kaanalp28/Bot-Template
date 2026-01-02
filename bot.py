# discord api
import discord 
from discord.ext import commands, bridge

# .env configuration
from dotenv import load_dotenv
load_dotenv()

# system
import psutil
import os

# custom utilities and setup
from Utilities import db, log

log = log.Logger("bot")

# bot runtime variable
token = os.getenv("BOT_TOKEN")

prefix = os.getenv("PREFIX")

class Bot(bridge.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # bot version
        self.Version = "0.1.0"

        # operational level variables
        self.Updating = False
        self.Debugging = False
        self.Maintaining = False

        # psutil utilization
        self.process = psutil.Process(os.getpid())

    @commands.Cog.listener()
    async def on_ready(self):
        await log.info(f"{self.user} is online.")
        await db.build()

# calling and initializing the bot
bot = bridge.AutoShardedBot(
    command_prefix=commands.when_mentioned_or(prefix),
    intents=discord.Intents.all(), 
    case_insensitive=True, 
    help_command=None,
    allowed_mentions=discord.AllowedMentions.all(),
    status=discord.Status.online,
    activity=discord.Game(name="Type {}help for more information!".format(prefix)),
)

# Load cogs
for subdir, dirs, files in os.walk("./Cogs"):
    for name in files:
        filepath = str(subdir + os.sep + name).replace(os.sep, ".")
        if filepath.endswith((".py")):
            bot.load_extension(filepath[2:-3])
        
bot.run(token, reconnect=True)