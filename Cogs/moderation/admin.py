import discord
import random
import asyncio
import typing
from datetime import timedelta
from discord import User, errors, TextChannel, Forbidden
from discord.ext import commands, bridge

dMember = discord.Member

class Admin(commands.Cog):
    def __init__(self, bot):
        bot.self = bot


    async def on_ready(self):
        print("Admin Cog was loaded successfully!")


    @bridge.bridge_command(
    name='purge',
    hidden=True,
    aliases=['clear'],
    description='Clears a specified number of messages.',
    usage='<number of messages to delete>',
    brief='Delete messages from the chat.'
    )
    @commands.check_any(commands.has_permissions(manage_messages=True), commands.is_owner())
    async def purge(self, ctx, amount=0):
        """Mass delete messages"""
        maxPurge = 500
        user_dict = {}
        sender = ctx.message.author
        if amount > maxPurge:
            await ctx.send("{} || Failed to purge messages! **(The max amount of messages you can purge is {}!)**".format(sender.mention, maxPurge))
        elif amount == 0:
            pass #send help message
        else:
            await ctx.message.delete()
            async for message in ctx.channel.history(limit=amount):
                if message.author.global_name != None:
                    user_string = str(message.author.global_name+" ("+message.author.name+")")
                elif message.author.nick != None:
                    user_string = str(message.author.nick+" ("+message.author.name+")")
                elif message.author.discriminator != None and message.author.discriminator != 0:
                    user_string = str(message.author.name+"#"+message.author.discriminator)
                else:
                    user_string = str(message.author.name)

                if user_string in user_dict:
                    user_dict[user_string] += 1
                else:
                    user_dict[user_string] = 1

            await ctx.channel.purge(limit=amount)
            formatted_output = "\n".join(f"**{name}**: {value}" for name, value in user_dict.items())
            print(formatted_output)
            total = sum(user_dict.values())
            print(total)
            if total == 1:
                firstline = "1 message was removed.\n\n"
            else:
                firstline = str(total)+" messages were removed.\n\n"
            await ctx.send(firstline+formatted_output, delete_after=2)

    @purge.error
    async def purge_handler(self, ctx, error):
        sender = ctx.message.author
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("{} || Failed to purge messages! **(You don't have permissions to use this command!)**".format(sender.mention))

    @bridge.bridge_command(
    name='purge_until',
    hidden=True,
    aliases=['clearuntil','purgeuntil','clear_until','purge_id','purgeid','clear_id','clearid'],
    description='Clears messages in a channel until a certain message is found.',
    usage='<message_id>',
    brief='Delete messages from the chat until a specific message.'
    )
    @commands.has_permissions(manage_messages=True)
    async def purge_until(self, ctx, message_id: int):
        """Clear messages in a channel until the given message_id. Given ID is not deleted"""
        channel = ctx.message.channel
        try:
            message = await channel.fetch_message(message_id)
        except errors.NotFound:
            await ctx.send("Message could not be found in this channel")
            return

        await ctx.message.delete()
        await channel.purge(after=message)
        return True
    
    @purge_until.error
    async def purge_until_handler(self, ctx, error):
        sender = ctx.message.author
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("{} || Failed to purge messages! **(You don't have permissions to use this command!)**".format(sender.mention))

    @bridge.bridge_command(
        name='purge_user',
        hidden=True,
        aliases=['purgeuser','clearuser','clear_user'],
        description='Clears messages from a user in every channel.',
        usage='<user> [n=5]',
        brief='Delete messages from a specific user.'
    )
    @commands.has_permissions(manage_messages=True)
    async def purge_user(self, ctx, user: User, num_minutes: typing.Optional[int] = 5):
        """Clear all messages of <User> in every channel within the last [n=5] minutes"""
        after = ctx.message.created_at - timedelta(minutes=num_minutes)

        def check(msg):
            return msg.author.id == user.id

        for channel in await ctx.guild.fetch_channels():
            if type(channel) is TextChannel:
                try:
                    await channel.purge(limit=100*num_minutes, check=check, after=after)
                except Forbidden:
                    continue

    @purge_user.error
    async def purge_user_handler(self, ctx, error):
        sender = ctx.message.author
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("{} || Failed to purge messages! **(You don't have permissions to use this command!)**".format(sender.mention))


    @bridge.bridge_command(
        name='viewlogs',
        hidden=True,
        aliases=['audit','auditlog'],
        description='View the audit log of the server.',
        usage='<user> [reason]',
        brief='View the logs. Default is 30.'
    )
    @commands.has_permissions(view_audit_log=True)
    async def viewlogs(self, ctx, amount=30):
        """Views a number of audit logs."""
        returnval = f"```Entry ID    -   Performer   -   Action  -   Target"
        async for entry in ctx.message.guild.audit_logs(limit=amount):
            if str(entry.action) in ["AuditLogAction.kick", "AuditLogAction.ban", "AuditLogAction.member_role_update"]:
                returnval += f"\n{entry.id} - {entry.user.name}#{entry.user.discriminator} - {entry.action} - {entry.target.name}#{entry.target.discriminator}"
            else:
                returnval += f"\n{entry.id} - {entry.user.name}#{entry.user.discriminator} - {entry.action}"
        returnval += "```"
        await ctx.send(returnval)
    
    @viewlogs.error
    async def log_handler(self, ctx, error):
        sender = ctx.message.author
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("{} || Failed to read audit logs! **(You don't have permissions to use this command!)**".format(sender.mention))

    @bridge.bridge_command(
        name='kick',
        hidden=True,
        aliases=['kickmember'],
        description='Kicks a member from the server.',
        usage='<user> [reason]',
        brief='Kick a member from the server.'
    )
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user: dMember, override=""):
        """kicks members"""
        sender = ctx.message.author
        if sender.top_role == user.top_role:
            if sender == user and override != "override":
                await ctx.send("{} || You can't kick yourself!".format(sender.mention))
                await ctx.send(f"Well I mean you could. Put override on the end of the command to kick yourself.")
            elif sender == user and override == "override":
                try:
                    await ctx.send(f"{sender.mention} is kicking themself.")
                    await dMember.kick(user, reason=None)
                except Exception as e:
                    await ctx.send(f"Error: {e}")
            else:
                await ctx.send("{} || Can't kick someone who has the same role as yours.".format(sender.mention))
        else:
            if sender.top_role < user.top_role:
                await ctx.send("{} || Can't kick a role that's higher than yours!".format(sender.mention))
            else:
                await ctx.send("{} || Sucessfully kicked **{}**".format(sender.mention, user))
                await dMember.kick(user, reason=None)

    @kick.error
    async def kick_handler(self, ctx, error):
        sender = ctx.message.author
        try:
            if error.param.name == 'user':
                await ctx.send("{} || You need to mention someone to kick.".format(sender.mention))
        except: pass
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("{} || You don't have the permissions to use that command!".format(sender.mention))

    @bridge.bridge_command(
        name='ban',
        hidden=True,
        aliases=['banmember'],
        description='Bans a member from the server.',
        usage='<user_id>',
        brief='Ban a member from the server.'
    )
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: dMember, *, banreason):
        """bans members"""
        sender = ctx.message.author
        if sender.top_role == user.top_role:
            await ctx.send("{} || Can't ban someone who has the same role as yours.".format(sender.mention))
        else:
            if sender.top_role < user.top_role:
                await ctx.send("{} || Can't ban a role that's higher than yours!".format(sender.mention))
            else:
                if sender == user:
                    await ctx.send("{} || You can't ban yourself!".format(sender.mention))
                else:
                    await ctx.send("{} || Sucessfully banned **{}** for {}".format(sender.mention, user, banReason))
                    await dMember.ban(user, reason=banreason)

    @ban.error
    @commands.has_permissions(ban_members=True)
    async def ban_handler(self, ctx, error):
        sender = ctx.message.author
        try:
            if error.param.name == 'user':
                await ctx.send("{} || You need to mention someone to ban.".format(sender.mention))
            if error.param.name == 'banreason':
                await ctx.send("{} || You need to give a reason to ban that user.".format(sender.mention))
        except: pass
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("{} || You don't have the permissions to use that command!")


    @bridge.bridge_command(
        name='lock',
        hidden=True,
        aliases=['lockchannel'],
        description='Locks the current channel to prevent members from sending messages.',
        usage='[channel]',
        brief='Lock a channel to restrict messages.'
    )
    @commands.check_any(commands.has_permissions(manage_channels=True), commands.is_owner())
    async def lock(self, ctx, channel: discord.TextChannel = None):
        """
        Locks a specified channel (or the current channel if none is provided) by removing the @everyone send message permission.
        """
        channel = channel or ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        if overwrite.send_messages is False:
            await ctx.send(f'⚠️ {channel.mention} is already locked.')
            return
        overwrite.send_messages = False
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send(f'🔒 {channel.mention} has been locked.')

    @lock.error
    @commands.check_any(commands.has_permissions(manage_channels=True), commands.is_owner())
    async def lock_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You do not have permission to lock channels.")
        elif isinstance(error, commands.ChannelNotFound):
            await ctx.send("❌ Channel not found.")
        else:
            await ctx.send("❌ An error occurred while locking the channel.")


    @bridge.bridge_command(
        name='unlock',
        hidden=True,
        aliases=['unlockchannel'],
        description='Unlocks the current channel to allow members to send messages.',
        usage='[channel]',
        brief='Unlock a channel to allow messages.'
    )
    @commands.check_any(commands.has_permissions(manage_channels=True), commands.is_owner())
    async def unlock(self, ctx, channel: discord.TextChannel = None):
        print(channel)
        """
        Unlocks a specified channel (or the current channel if none is provided) by allowing the @everyone send message permission.
        """
        channel = channel or ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        if overwrite.send_messages is True:
            await ctx.send(f'⚠️ {channel.mention} is already unlocked.')
            return
        overwrite.send_messages = True
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send(f'🔓 {channel.mention} has been unlocked.')

    @unlock.error
    @commands.check_any(commands.has_permissions(manage_channels=True), commands.is_owner())
    async def unlock_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You do not have permission to unlock channels.")
        elif isinstance(error, commands.ChannelNotFound):
            await ctx.send("❌ Channel not found.")
        else:
            await ctx.send("❌ An error occurred while unlocking the channel.")


def setup(bot):
    bot.add_cog(Admin(bot))