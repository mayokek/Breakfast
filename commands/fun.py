import asyncio
import random
import os
import discord

from discord.ext import commands

class Fun():
    def __init__(self, bot):
        self.bot = bot
        self.poll_session = []

    @commands.command(pass_context=True)
    async def rate(self, ctx, user:discord.User=None):
        """Have the bot rate yourself or another user"""
        if user is None or user.id == ctx.message.author.id:
            await self.bot.say("I rate you a 10/10")
        elif user == self.bot.user:
            await self.bot.say("I rate myself a 11/10")
        else:
            await self.bot.say("I rate {} a {}/10".format(user.name, random.randint(0, 10)))

    @commands.command(pass_context=True, no_pm=True)
    async def poll(self, ctx, *text):
        """Starts/Stops a poll"""
        message = ctx.message
        if len(text) == 1:
            if text[0].lower() == "stop":
                await self.endpoll(message)
                return
        if not self.getPollByChannel(message):
            check = " ".join(text).lower()
            if "@everyone" in check or "@here" in check:
                await self.bot.say("Nice try.")
                return
            p = NewPoll(message, self)
            if p.valid:
                self.poll_session.append(p)
                await p.start()
            else:
                await self.bot.say("b$poll question/option1/option2/...")
        else:
            await self.bot.say("A poll is already ongoing in this channel")

    @commands.command(pass_context=True)
    async def vote(self, ctx, *, vote:int):
        """Vote

        Only works when the poll is going"""
        if self.getPollByChannel(ctx.message):
            try:
                await self.check_poll_votes(ctx.message)
                await self.bot.say(":ballot_box: Thanks for voting, your vote has been recorded!")
            except:
                await self.bot.say(":warning: Something went wrong when casting your vote")
        else:
            await self.bot.say("There's no poll ongoing in this channel")

    async def endpoll(self, message):
        if self.getPollByChannel(message):
            p = self.getPollByChannel(message)
            if p.author == message.author.id:
                await self.getPollByChannel(message).endPoll()
            else:
                await self.bot.say(":no_entry_sign: Only the poll creator can end the poll")
        else:
            await self.bot.say("There's no poll ongoing in this channel")

    def getPollByChannel(self, message):
        for poll in self.poll_session:
            if poll.channel == message.channel:
                return poll
        return False

    async def check_poll_votes(self, message):
        if message.author.id != self.bot.user.id:
            if self.getPollByChannel(message):
                self.getPollByChannel(message).checkAnswer(message)

class NewPoll():
    def __init__(self, message, main):
        self.channel = message.channel
        self.author = message.author.id
        self.client = main.bot
        self.poll_session = main.poll_session
        msg = message.content[6:]
        msg = msg.split("/")
        if len(msg) < 2:
            self.valid = False
            return None
        else:
            self.valid = True
        self.already_voted = []
        self.question = msg[0]
        msg.remove(self.question)
        self.answers = {}
        i = 1
        for answer in msg:
            self.answers[i] = {"ANSWER":answer, "VOTES":0}
            i += 1

    async def start(self):
        msg = "**:ballot_box: THE VOTE HAS BEGUN!**\n\n**Current question:** {}\n\n".format(self.question)
        for id, data in self.answers.items():
            msg += "`[{}]` `{}`\n".format(id, data["ANSWER"])
        msg += "\n:information_source: Type `b$vote {number}` to vote!"
        await self.client.send_message(self.channel, msg)
        await asyncio.sleep(300) # Goes for 5 minutes
        if self.valid:
            await self.endPoll()

    async def endPoll(self):
        self.valid = False
        msg = "**:ballot_box: THE VOTE HAS ENDED!**\n\n**Current Question:** {}\n\n".format(self.question)
        for data in self.answers.values():
            msg += "`{}` has `{}` votes\n".format(data["ANSWER"], str(data["VOTES"]))
        await self.client.send_message(self.channel, msg)
        self.poll_session.remove(self)

    def checkAnswer(self, message):
        try:
            i = int(message.content.replace("b$vote ", ""))
            if i in self.answers.keys():
                if message.author.id not in self.already_voted:
                    data = self.answers[i]
                    data["VOTES"] += 1
                    self.answers[i] = data
                    self.already_voted.append(message.author.id)
        except ValueError:
            pass

def setup(bot):
    bot.add_listener(Fun(bot).check_poll_votes, "on_message")
    bot.add_cog(Fun(bot))

