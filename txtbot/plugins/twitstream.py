from discord.ext import commands
from twitter import *
import asyncio
import random


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

        print(f'[TwitStream Prompted]: {ctx.message.author}: twit {screen_name} {count}')
        if int(count) > 150:
            async with ctx.typing():
                await asyncio.sleep(1)
                await ctx.send('[TwitStream Error]: Too many tweets requested')
                await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')
        else:
            num = int(count) - 1

            data = self.t.statuses.user_timeline(screen_name=screen_name, count=count, tweet_mode="extended")
            twit_id = data[num]["id"]

            async with ctx.typing():
                await asyncio.sleep(1)
                await ctx.send(f'https://twitter.com/{screen_name}/status/{twit_id}')
                print(f'[TwitStream Returned]: https://twitter.com/{screen_name}/status/{twit_id}')
                await ctx.message.add_reaction('\N{THUMBS UP SIGN}')

    @commands.command(pass_context=True)
    async def trump(self, ctx):
        count = random.randint(1, 50)
        num = int(count) - 1

        print(f'[TwitStream Prompted]: {ctx.message.author}: trump')

        data = self.t.statuses.user_timeline(screen_name="realDonaldTrump", count=count, tweet_mode="extended")
        twit_id = data[num]["id"]
        async with ctx.typing():
            await asyncio.sleep(1)
            await ctx.send(f'https://twitter.com/realDonaldTrump/status/{twit_id}')
            print(f'[TwitStream Returned]: https://twitter.com/realDonaldTrump/status/{twit_id}')
            await ctx.message.add_reaction('\N{THUMBS UP SIGN}')


def setup(bot):
    bot.add_cog(TwitStream(bot))
