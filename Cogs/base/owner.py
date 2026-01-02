# discord api
from discord.ext import commands
from discord.commands import slash_command, Option
from discord.ext.commands import is_owner

# system
import os
import sys
from dotenv import load_dotenv

# custom utilities
from Utilities import log
log = log.Logger("owner")

# grab home guild from '.env' and typecast horribly lol
GuildID = os.getenv("GUILD_ID")
Home_Guild = int(GuildID)

class Admin2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await log.info("Owner cog loaded.")
    
    # Load
    @commands.slash_command(
        guild_ids=[Home_Guild],
        description="Load an extension | owner-only command"
    )
    @commands.is_owner() 
    async def load(
        self, 
        context,
        extension: Option(
            str,
            "Select the extension to load", 
            required=True,
            choices=[
                "errors", "owner"
            ]
        )
    ):
        self.bot.load_extension(f"Cogs.{extension}")
        await context.respond(
            f"Loaded extension: `{extension}`"
        )
        await log.info(f"Loaded extension: {extension}")

    # Unload
    @commands.slash_command(
        guild_ids=[Home_Guild],
        description="Unload an extension | owner-only command"
    )
    @commands.is_owner() 
    async def unload(
        self, 
        context,
        extension: Option(
            str,
            "Select the extension to unload", 
            required=True,
            choices=[
                "errors", "owner"
            ]
        )
    ):
        self.bot.unload_extension(f"Cogs.{extension}")
        await context.respond(
            f"Unloaded extension: `{extension}`"
        )
        await log.info(f"Unloaded extension: {extension}")

    # Reload
    @commands.slash_command(
        guild_ids=[Home_Guild],
        description="Reload an extension | owner-only command"
    )
    @commands.is_owner() 
    async def reload(
        self, 
        context,
        extension: Option(
            str,
            "Select the extension to reload", 
            required=True,
            choices=[
                "errors", "owner"
            ]
        )
    ):
        self.bot.reload_extension(f"Cogs.{extension}")
        await context.respond(
            f"Reloaded extension: `{extension}`"
        )
        await log.info(f"Reloaded extension: {extension}")

    # Shutdown
    @commands.slash_command(
        guild_ids=[Home_Guild],
        description="Shutdown the bot | owner-only command"
    )
    @commands.is_owner()
    async def shutdown(
        self,
        context
    ):
        await context.respond(
            "Shutting down."
        )
        await log.info("Shutting down.")
        await self.bot.close()

    # Restart 
    @commands.slash_command(
        guild_ids=[Home_Guild],
        description="Restart the bot | owner-only command"
    )
    @commands.is_owner()
    async def restart(
        self,
        context
    ):
        await context.respond(
            "Restarting..."
        )
        await log.info("Restarting...")
        await self.bot.close()
        os.execl(sys.executable, sys.executable, *sys.argv)

def setup(bot):
    bot.add_cog(Admin2(bot))