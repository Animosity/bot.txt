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
    async def tweet(self, ctx, screen_name, count=None):
        if count is None:
            count = 1

        if int(count) > 100:
            async with ctx.typing():
                await asyncio.sleep(1)
                await ctx.send('wow too much bro')
                await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')
        else:
            numvar = int(count) - 1
            x = self.t.statuses.user_timeline(screen_name=screen_name, count=count)

            date_string = datetime.strptime(x[numvar]["created_at"], '%a %b %d %H:%M:%S %z %Y').replace(
                tzinfo=timezone.utc).astimezone(tz=None).strftime('%I:%M:%S %m-%d-%y')

            profile_image = x[0]["user"]["profile_image_url_https"]

            e = discord.Embed()
            e.set_image(url=profile_image)
            e.add_field(name=date_string, value=x[numvar]["text"], inline=True)
            e.set_author(name=f'@{x[0]["user"]["screen_name"]}')

            print(profile_image)

            async with ctx.typing():
                await asyncio.sleep(1)
                await ctx.send(embed=e)
                await ctx.message.add_reaction('\N{THUMBS UP SIGN}')

    @commands.command(pass_context=True)
    async def trump(self, ctx):
        count = random.randint(1, 50)
        numvar = int(count) - 1
        x = self.t.statuses.user_timeline(screen_name="realDonaldTrump", count=count, tweet_mode="extended")

        date_string = datetime.strptime(x[numvar]["created_at"], '%a %b %d %H:%M:%S %z %Y').replace(
            tzinfo=timezone.utc).astimezone(tz=None).strftime('%I:%M:%S %m-%d-%y')

        profile_image = x[0]["user"]["profile_image_url_https"]

        e = discord.Embed()
        e.set_thumbnail(url=profile_image)
        e.add_field(name=date_string, value=x[numvar]["full_text"], inline=True)
        e.set_author(name=f'@{x[0]["user"]["screen_name"]}')
        e.set_footer(text=f'Requested by: {ctx.message.author}')
        async with ctx.typing():
            await asyncio.sleep(1)
            await ctx.send(embed=e)
            await ctx.message.add_reaction('\N{THUMBS UP SIGN}')


def setup(bot):
    bot.add_cog(TwitStream(bot))
