import discord
from discord.ext import commands


class Simple(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def cool(self, ctx):
        async with ctx.typing():
            await ctx.send('im cool 8-)')


def setup(bot):
    bot.add_cog(Simple(bot))
