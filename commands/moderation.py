import asyncio
import discord

from discord.ext import commands
from util.mysql import *
from util.logging import logging
from util.embed import *
from util import checks

class Moderation():
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging(bot)

    @commands.command(pass_context=True)
    @checks.is_mod()
    async def kick(self, ctx, user:discord.Member, *, reason:str=None):
        """Kick a user from the server"""
        if reason is None:
            reason = "Reason is empty"
        try:
            await self.bot.kick(user)
        except discord.errors.Forbidden:
            await self.bot.say("I may not kick this user as I don't have the `Kick Members` pemission!")
            return
        await self.bot.send_typing(ctx.message.channel)
        fields = {"User kicked":user, "Reason":reason, "Kicked by":ctx.message.author}
        embed = make_list_embed(fields)
        embed.title = "Moderator Action"
        embed.color = 0xFF0000
        embed.set_thumbnail(url="http://img15.deviantart.net/c8c3/i/2012/358/4/b/mdt_flying_kick_by_mdtartist83-d4j0sef.png")
        await self.logger.embed_mod_log(ctx.message.server, embed)
        await self.bot.say("Successfully kicked `{}`".format(user))

    @commands.command(pass_context=True)
    @checks.is_mod()
    async def ban(self, ctx, user:discord.Member, *, reason:str=None):
        """Ban a user from the server"""
        if reason is None:
            reason = "Reason is empty"
        try:
            await self.bot.ban(user, delete_message_days=0)
        except discord.errors.Forbidden:
            await self.bot.say("I may not ban this user as I don't have the `Ban Members` permission!")
            return
        await self.bot.send_typing(ctx.message.channel)
        fields = {"User banned":user, "Reason":reason, "Banned by":ctx.message.author}
        embed = make_list_embed(fields)
        embed.title = "Moderator Action"
        embed.color = 0xFF0000
        embed.set_thumbnail(url="http://vignette3.wikia.nocookie.net/bakuganrandomtalk/images/b/ba/BanHammer.v2.png")
        await self.logger.embed_mod_log(ctx.message.server, embed)
        await self.bot.say("Successfully banned `{}`".format(user))

    @commands.command(pass_context=True)
    @checks.is_mod()
    async def prune(self, ctx, amount:int):
        """Prunes the specified amount of messages"""
        try:
            await self.bot.delete_message(ctx.message)
        except discord.errors.Forbidden:
            await self.bot.say("Cannot prune as I don't have the `Manage Messages` permission!")
            return
        deleted = await self.bot.purge_from(ctx.message.channel, limit=amount)
        await self.bot.say("{} pruned {} messages!".format(ctx.message.author.mention, len(deleted)))
        
def setup(bot):
    bot.add_cog(Moderation(bot))
