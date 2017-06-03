import discord

def make_msg_embed(author, color, msg, *, formatUser=False, useNick=False):
    if formatUser:
        name = str(author)
    else:
        if useNick:
            name = author.display_name
    embed = discord.Embed(color=color, description=message)
    return embed

def make_list_embed(fields):
    embed = discord.Embed(description="\u200b")
    for key, value in fields.items():
        embed.add_field(name=key, value=value, inline=True)
    return embed
