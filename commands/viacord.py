import asyncio
import discord
from discord.ext import commands
from collections import namedtuple
from util.chat_formatting import escape, pagify

OpenCall = namedtuple("ViaCord", ["source", "destination"])

class ViaCord:
    """Communicate with other servers/channels"""

    def __init__(self, bot):
        self.bot = bot
        self.open_calls = {}

    @commands.command(pass_context=True)
    async def viacord(self, ctx, channel):
        """Makes you able to communicate with other servers/channels"""
        author = ctx.message.author
        chann = ctx.message.channel

        def check(m):
            try:
                return channels[int(m.context)]
            except:
                return False

        channels = self.bot.get_all_channels()
        channels = [c for c in channels if c.name.lower() == channel or c.id == channel]
        channels = [c for c in channels if c.type == discord.ChannelType.text]

        if not channels:
            await self.bot.say("No channel found! Remember to type just the channel name, no `#`")
            return

        if len(channels) > 1:
            msg = "Multiple results found.\nChoose a server:\n"
            for i, channel in enumerate(channels):
                msg += "`{} - {} ({})\n`".format(i, channel.server, channel.id)
            for page in pagify(msg):
                await self.bot.say(page)
            choice = await self.bot.wait_for_message(author=author,
                                                      timeout=20,
                                                      check=check,
                                                      channel=chann)
            if choice is None:
                await self.bot.say("Oh, nevermind then!")
                return
            channel = channels[int(choice.content)]
        else:
            channel = channels[0]

        viacord = OpenCall(source=chann, destination=channel)

        self.open_calls[author] = viacord
        await self.bot.say("A ViaCord connection has been opened!\nEverything you say"
                           " will relayed to the channel.\n"
                           "Reponses will be relayed here.\nType"
                           " `viacord exit` to quit.")
        await self.bot.send_message(channel, "The ViaCord has been opened from {} by {}".format(ctx.message.server.name, author.name))
            

    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        for k, v in self.open_calls.items():
            if v.destination == message.channel:
                msg = "{}: {}".format(message.author.name, message.content)
                msg = escape(msg, mass_mentions=True)
                await self.bot.send_message(v.source, msg)
            if v.source == message.channel:
                if message.content.lower() == "viacord exit":
                    await self.bot.send_message(v.destination, "The ViaCord connection has been terminated on another end!")
                    await self.bot.send_message(v.source, "The ViaCord connection has been terminated!")
                    await asyncio.sleep(2)
                    del self.open_calls[k]
                    return
                if "b$" in message.content:
                    return
                msg = "{}: {}".format(message.author.name, message.content)
                msg = escape(msg, mass_mentions=True)
                await self.bot.send_message(v.destination, msg)

def setup(bot):
    bot.add_cog(ViaCord(bot))
