import discord

from discord.ext import commands
from util.config import Config
from util.mysql import *
config = Config()

class owner_only(commands.CommandError):
    pass

class not_server_owner(commands.CommandError):
    pass

class not_bot_commander(commands.CommandError):
    pass

class not_mod(commands.CommandError):
    pass

def is_owner():
    def predicate(ctx):
        if ctx.message.author.id == config.owner_id:
            return True
        else:
            raise owner_only
    return commands.check(predicate)

def is_server_owner():
    def predicate(ctx):
        if ctx.message.author.id == ctx.message.server.owner_id:
            return True
        else:
            raise not_server_owner
    return commands.check(predicate)

def is_bot_commander():
    def predicate(ctx):
        role = discord.utils.get(ctx.message.author.roles, name="Breakfast Eater")
        if role:
            return True
        else:
            raise not_bot_commander
    return commands.check(predicate)

def is_mod():
    def predicate(ctx):
        name = read_data_entry(ctx.message.server.id, "mod-role")
        role = discord.utils.get(ctx.message.author.roles, name=name)
        if role:
            return True
        else:
            raise not_mod
    return commands.check(predicate)
