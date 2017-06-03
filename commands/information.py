import asyncio
import discord
import time

from discord.ext import commands

class Information():
    def __init__(self, bot):
        self.bot = bot

        
    
def setup(bot):
    bot.add_cog(Information(bot))
