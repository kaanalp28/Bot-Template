# discord api
import discord
from discord.ext import commands

from discord.ext import commands, bridge
from discord.ext.commands import Context
from discord.ext.bridge import BridgeContext

# custom utilities
from Utilities import log
log = log.Logger("PingBot")

class PingBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await log.info("Ping-Bot cog loaded.")

    @bridge.bridge_command(
        name="ping",
        description="Shows the bot's latency.",
        help="Ping the bot to see the latency!",
        aliases=["t1","pong"],
        )
    async def test(self, ctx: BridgeContext):
        await ctx.send('Pong! {0}'.format(round(self.bot.latency, 1)))

def setup(bot):
    bot.add_cog(PingBot(bot))


    #mongodb+srv://kaanalp28:<password>@cluster0.tc9lg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0