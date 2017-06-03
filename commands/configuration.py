from discord.ext import commands
from util.mysql import *
from util.embed import *

class Configuration():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def config(self, ctx, type:str, *, value:str):
        """Modifies the server's local config"""
        if ctx.message.author is not ctx.message.server.owner:
            await self.bot.say("Only the server owner (`{}`) can use this command.".format(ctx.message.server.owner))
            return
        await self.bot.send_typing(ctx.message.channel)
        if type == "mod-role" or type == "mute-role" or type == "auto-role" or type == "join-leave-channel":
            update_data_entry(ctx.message.server.id, type, value)
            await self.bot.say("Successfully set the {} to `{}`".format(type, value))
        else:
            await self.bot.say("`{}` is not a valid type!".format(type))

    @commands.command(pass_context=True)
    async def showconfig(self, ctx):
        """Shoes the local server's configuration"""
        await self.bot.send_typing(ctx.message.channel)
        mod_role = read_data_entry(ctx.message.server.id, "mod-role")
        mute_role = read_data_entry(ctx.message.server.id, "mute-role")
        auto_role = read_data_entry(ctx.message.server.id, "auto-role")
        join_leave = read_data_entry(ctx.message.server.id, "join-leave-channel")
        fields = {"Mod Role":mod_role, "Mute Role":mute_role, "Auto Role":auto_role, "Join/Leave Channel":join_leave}
        embed = make_list_embed(fields)
        embed.title = "Server Configuration"
        embed.color = 0xFF0000
        await self.bot.say(embed=embed)

def setup(bot):
    bot.add_cog(Configuration(bot))
        
