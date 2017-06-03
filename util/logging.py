import discord

from util.logger import log

class logging():
    def __init__(self, bot):
        self.bot = bot

    async def mod_log(self, server, msg):
        log_to = discord.utils.get(server.channels, name="mod-log")
        if log_to:
            try:
                await self.bot.send_message(log_to, ":crystal_ball:: {}".format(msg), embed=embed)
            except:
                pass

    async def embed_mod_log(self, server, embed:discord.Embed):
        log_to = discord.utils.get(server.channels, name="mod-log")
        if log_to:
            try:
                await self.bot.send_message(log_to, embed=embed)
            except discord.HTTPException:
                await self.bot.send_message(log_to, ":warning: Failed to send embed message\nI need `Embed Links` permission")
