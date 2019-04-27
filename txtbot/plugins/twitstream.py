import discord
from discord.ext import commands
from twitter import *
import asyncio
import random
from datetime import datetime, timezone


class TwitStream(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = self.bot.config["TWITSTREAM"]
        self.consumer_key = self.config["CONSUMER_KEY"]
        self.consumer_secret = self.config["CONSUMER_SECRET"]
        self.token_key = self.config["TOKEN_KEY"]
        self.token_secret = self.config["TOKEN_SECRET"]

        self.t = Twitter(auth=OAuth(self.token_key, self.token_secret, self.consumer_key, self.consumer_secret))

    @commands.command(pass_context=True)
    async def twit(self, ctx, screen_name, count=None):
        if count is None:
            count = 1

        if int(count) > 150:
            async with ctx.typing():
                await asyncio.sleep(1)
                await ctx.send('[TwitStream Error]: Too many tweets requested')
                await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')
        else:
            num = int(count) - 1
            data = self.t.statuses.user_timeline(screen_name=screen_name, count=count)

            date_string = datetime.strptime(data[num]["created_at"], '%a %b %d %H:%M:%S %z %Y').replace(
                tzinfo=timezone.utc).astimezone(tz=None).strftime('%I:%M:%S %m-%d-%y')

            e = discord.Embed()
            e.set_thumbnail(url=data[0]["user"]["profile_image_url"])
            e.add_field(name=date_string, value=data[num]["text"], inline=True)
            e.set_author(name=f'@{data[0]["user"]["screen_name"]}')

            async with ctx.typing():
                await asyncio.sleep(1)
                await ctx.send(embed=e)
                await ctx.message.add_reaction('\N{THUMBS UP SIGN}')

    @commands.command(pass_context=True)
    async def trump(self, ctx):
        count = random.randint(1, 50)
        num = int(count) - 1
        data = self.t.statuses.user_timeline(screen_name="realDonaldTrump", count=count, tweet_mode="extended")

        date_string = datetime.strptime(data[num]["created_at"], '%a %b %d %H:%M:%S %z %Y').replace(
            tzinfo=timezone.utc).astimezone(tz=None).strftime('%I:%M:%S %m-%d-%y')

        e = discord.Embed()
        e.set_thumbnail(url=data[0]["user"]["profile_image_url"])
        e.add_field(name=date_string, value=data[num]["full_text"], inline=True)
        e.set_author(name=f'@{data[0]["user"]["screen_name"]}')

        async with ctx.typing():
            await asyncio.sleep(1)
            await ctx.send(embed=e)
            await ctx.message.add_reaction('\N{THUMBS UP SIGN}')


def setup(bot):
    bot.add_cog(TwitStream(bot))
