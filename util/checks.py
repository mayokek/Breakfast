from discord.ext import commands
from util.config import Config
config = Config()

def is_owner_check(user):
    return user.id == config.owner_id

def is_owner():
    return commands.check(lambda ctx: is_owner_check(ctx.message.author))
