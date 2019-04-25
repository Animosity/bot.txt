from discord.ext import commands
from twitter import *
import asyncio


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
    async def tweet(self, ctx, username):
        x = self.t.statuses.user_timeline(screen_name=username, count=1)
        async with ctx.typing():
            await asyncio.sleep(1)
            await ctx.send(f'{x[0]["user"]["screen_name"]}: {x[0]["text"]}')
            await ctx.message.add_reaction('\N{THUMBS UP SIGN}')


def setup(bot):
    bot.add_cog(TwitStream(bot))
