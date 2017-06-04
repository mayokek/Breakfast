import asyncio
import aiohttp
import time
import sys
import subprocess
import os
import discord

start_time = time.time()

from util.logger import log
log.init()

from datetime import datetime
from discord.ext import commands
from util.config import Config
from util import checks
from util.chat_formatting import pagify, box
from util.embed import *
from util.mysql import *
from util.logging import logging

config = Config()
bot = commands.Bot(command_prefix=config.command_prefix, description="A multi-purpose bot", pm_help=False)
i = datetime.now()
logger = logging(bot)
lock_status = False

extensions = ["commands.fun", "commands.moderation", "commands.configuration", "commands.information", "commands.viacord"]

xl = "```xl\n{}\n```"

async def _restart_bot():
	await bot.logout()
	subprocess.call([sys.executable, "bot.py"])
	
async def _shutdown_bot():
	await bot.logout()

async def set_default_status():
        game = discord.Game(name="eating Breakfast", url="http://twitch.tv/FUNDRAGON123", type=1)
        await bot.change_presence(status=discord.Status.online, game=game)
	
@bot.event
async def on_resumed():
	log.info("Reconnected to discord")
	
@bot.event
async def on_ready():
	print("Bot connected!\n")
	print("Logged in as:\n{}/{}#{}\n".format(bot.user.id, bot.user.name, bot.user.discriminator))
	await set_default_status()
	for extension in extensions:
		try:
			bot.load_extension(extension)
		except Exception as e:
			log.error("Failed to load extension {}\n{}: {}".format(extension, type(e).__name__, e))

@bot.event
async def on_command_error(error, ctx):
        if isinstance(error, commands.CommandNotFound):
                return

        if isinstance(error, checks.owner_only):
                await bot.send_message(ctx.message.channel, ":no_entry: This command can only be ran by the bot owner")
                return
        if isinstance(error, checks.not_server_owner):
                await bot.send_message(ctx.message.channel, ":no_entry: This command can only be ran by the server owner (`{}`)".format(ctx.message.server.owner))
                return
        if isinstance(error, checks.not_bot_commander):
                await bot.send_message(ctx.message.channel, ":no_entry: You must have the `Breakfast Eater` role in order to use this command!")
                return

        if ctx.message.channel.is_private:
                await bot.send_message(ctx.message.channel, "An occur occured! Please try excuting this command on a server.")
                return

        try:
                await bot.send_message(ctx.message.channel, error)
        except:
                pass
        log.error("An error occured while executing the {} command: {}".format(ctx.command.qualified_name, error))

@bot.event
async def on_command(command, ctx):
        if ctx.message.channel.is_private:
                server = "PM"
        else:
                server = "{}/{}".format(ctx.message.server.id, ctx.message.server.name)
        print("[Command] [{}] [{}/{}]: {}".format(server, ctx.message.author.id, ctx.message.author, ctx.message.content))
        

@bot.event
async def on_message(message):
        if message.author.bot:
                return
        if isinstance(message.author, discord.Member):
                if discord.utils.get(message.author.roles, id=read_data_entry(message.author.server.id, "mute-role")):
                        return
        if getblacklistuser(message.author.id) is not None:
                return
        await bot.process_commands(message)

@bot.command(pass_context=True)
async def notifydev(ctx, *, message:str):
        """Sends a message to the developer/creator/owner"""
        if ctx.message.channel.is_private:
                server = "Sent via PM!"
        else:
                server = "Sent from {}/{}".format(ctx.message.server.id, ctx.message.server.name)
        await bot.send_message(discord.User(id=config.owner_id), "You have a new message! The user is `{}/{}` | `{}`\nMessage: {}".format(ctx.message.author.id, ctx.message.author, server, message))
        await bot.say("Message sent!")

@bot.command(hidden=True, pass_context=True)
@checks.is_owner()
async def restart(ctx):
        """Restart the bot"""
        await bot.say("Restarting...")
        log.warning("{} has restarted the bot!".format(ctx.message.author))
        await _restart_bot()

@bot.command(hidden=True, pass_context=True)
@checks.is_owner()
async def shutdown(ctx):
        """Stop the bot"""
        await bot.say("Shutting down...")
        log.warning("{} has stopped the bot!".format(ctx.message.author))
        await _shutdown_bot()

@bot.command(hidden=True, pass_context=True)
@checks.is_owner()
async def reply(ctx, id:str, message:str):
        """Reply something back"""
        await bot.send_message(discord.User(id=id), "[REPLY] From `Mayo#1149`\nMessage: `{}`".format(message))
        await bot.say("Message sent")

@bot.command(hidden=True, pass_context=True)
@checks.is_owner()
async def terminal(ctx, *, command:str):
        """Runs terminal commands and shows the ouput"""
        try:
                await bot.send_typing(ctx.message.channel)
                await bot.say(box(os.popen(command).read(), "xl"))
        except:
                await bot.say("Error, couldn't send command")

@bot.command(pass_context=True)
@checks.is_owner()
async def lockstatus(ctx):
        global lock_status
        if lock_status is True:
                lock_status = False
                await bot.say("Successfully changed the lock status to `false`")
        else:
                lock_status = True
                await bot.say("Successfully changed the lock status to `true`")

@bot.command(pass_context=True)
@checks.is_owner()
async def status(ctx, status=None, *, game=None):
        """Sets Breakfast's status

        Statuses: online, idle, dnd, invis"""

        statuses = {
                "online": discord.Status.online,
                "idle": discord.Status.idle,
                "dnd": discord.Status.dnd,
                "invis": discord.Status.invisible
                }
        if lock_status is True and ctx.message.author.id is not config.owner_id:
                await bot.say(":lock: The status is current locked!")
                return

        current_game = ctx.message.server.me.game if ctx.message.server is not None else None
        
        if status is not None and game is None:
                s = statuses.get(status.lower(), None)
                if s:
                        await bot.change_presence(status=s, game=current_game)
                        await bot.say("Successfully changed the status to `{}`".format(status))
        elif status is not None and game is not None:
                s = statuses.get(status.lower(), None)
                game = game.strip()
                if s:
                        await bot.change_presence(status=s, game=discord.Game(name=game))
                        await bot.say("Successfully changed the status to `{}` and game to `{}`".format(status, game))
        elif status is None and game is None:
                await bot.change_presence(status=discord.Status.online, game=None)
                await bot.say("Status has been reseted")

@bot.command(hidden=True, pass_context=True)
@checks.is_owner()
async def debug(ctx, *, code):
        """Evaluates code"""
        def check(m):
            if m.content.strip().lower() == "more":
                return True

        author = ctx.message.author
        channel = ctx.message.channel

        code = code.strip('` ')
        result = None

        global_vars = globals().copy()
        global_vars['bot'] = bot
        global_vars['ctx'] = ctx
        global_vars['message'] = ctx.message
        global_vars['author'] = ctx.message.author
        global_vars['channel'] = ctx.message.channel
        global_vars['server'] = ctx.message.server

        try:
            result = eval(code, global_vars, locals())
        except Exception as e:
            await bot.say(box('{}: {}'.format(type(e).__name__, str(e)),
                                   lang="py"))
            return

        if asyncio.iscoroutine(result):
            result = await result

        result = str(result)

        result = list(pagify(result, shorten_by=16))

        for i, page in enumerate(result):
            if i != 0 and i % 4 == 0:
                last = await self.bot.say("There are still {} messages. "
                                          "Type `more` to continue."
                                          "".format(len(result) - (i+1)))
                msg = await bot.wait_for_message(author=author,
                                                      channel=channel,
                                                      check=check,
                                                      timeout=10)
                if msg is None:
                    try:
                        await bot.delete_message(last)
                    except:
                        pass
                    finally:
                        break
            await bot.say(box(page, lang="py"))

@bot.command(hidden=True, pass_context=True)
@checks.is_owner()
async def blacklist(ctx, id:str, *, reason:str):
        """Blacklist an user"""
        await bot.send_typing(ctx.message.channel)
        user = discord.utils.get(list(bot.get_all_members()), id=id)
        if user is None:
                await bot.say("Could not find a user with an id of `{}`".format(id))
                return
        if getblacklistuser(id) != None:
                await bot.say("`{}` is already blacklisted".format(user))
                return
        blacklistuser(id, user.name, user.discriminator, reason)
        await bot.say("Successfully blacklisted `{}`".format(user))
        try:
                await bot.send_message(user, "You have been blacklisted by `{}` - Reason `{}`".format(ctx.message.author, reason))
        except:
                log.warning("Cannot send message to `{}`".format(user))
        fields = {"ID":id, "Name":user.name, "Discriminator":user.discriminator, "Reason":reason, "Time":i.strftime('%H:%M:%S %d/%m/%Y')}
        embed = make_list_embed(fields)
        embed.title = ":warning: Blacklist :warning:"
        embed.color = 0xFF0000
        await logger.embed_mod_log(ctx.message.server, embed)

@bot.command(hidden=True, pass_context=True)
@checks.is_owner()
async def unblacklist(ctx, id:str):
        """Unblacklist an user"""
        user = getblacklistuser(id)
        if user is None:
                await bot.say("No blacklisted user can be found with an id of `{}`".format(id))
                return
        try:
                unblacklistuser(id)
        except:
                await bot.say("No blacklisted user can be found with an id of `{}`".format(id))
        await bot.say("Successfully unblacklisted `{}#{}`".format(user.get("name"), user.get("discrim")))
        try:
                await bot.send_message(discord.User(id=id), "You have been unblacklisted by `{}`".format(ctx.message.author))
        except:
                log.warning("Cannot send message to `{}`".format(id))

@bot.command()
async def showblacklist():
        """Shows the list of users that are blacklisted"""
        blacklist = getblacklist()
        count = len(blacklist)
        if blacklist == []:
                blacklist = "No blacklisted users"
        else:
                blacklist = "\n".join(blacklist)
        await bot.say(xl.format("{} blacklisted users\n\n{}".format(count, blacklist)))

@bot.event
async def on_member_join(member:discord.Member):
        join_leave = read_data_entry(member.server.id, "join-leave-channel")
        auto_role = read_data_entry(member.server.id, "auto-role")
        if auto_role is None:
                return
        role = discord.utils.get(member.server.roles, id=auto_role)
        if role is not None:
                try:
                        await bot.add_roles(member, role)
                except:
                        None
        if join_leave is not None:
                join_leave_channel = discord.utils.get(member.server.channels, id=join_leave)
                if join_leave_channel is None:
                        update_data_entry(member.server.id, "join-leave-channel", None)
        else:
                join_leave_channel = None
        if join_leave_channel is not None:
                try:
                        fields = {"Name":member.name, "ID":member.id, "Discriminator":member.discriminator, "Joined At":i.strftime('%Y/%m/%d %H:%M:%S')}
                        embed = make_list_embed(fields)
                        embed.title = "Member Joined"
                        embed.color = 0x00FF00
                        embed.set_thumbnail(url=member.avatar_url)
                        await bot.send_message(join_leave_channel, embed=embed)
                except:
                        pass

@bot.event
async def on_member_leave(member:discord.Member):
        join_leave = read_data_entry(member.server.id, "join-leave-channel")
        if join_leave is not None:
                join_leave_channel = discord.utils.get(member.server.channels, id=join_leave)
                if join_leave_channel is None:
                        update_data_entry(member.server.id, "join-leave-channel", None)
        else:
                join_leave_channel = None
        if join_leave_channel is not None:
                try:
                        fields = {"Name":member.name, "ID":member.id, "Discriminator":member.discriminator, "Left At":i.strftime('%Y/%m/%d %H:%M:%S')}
                        embed = make_list_embed(fields)
                        embed.title = "Member Left"
                        embed.color = 0xFF0000
                        embed.set_thumbnail(url=member.avatar_url)
                        await bot.send_message(join_leave_channel, embed=embed)
                except:
                        pass
        

print("Connecting...")
bot.run(config._token)
