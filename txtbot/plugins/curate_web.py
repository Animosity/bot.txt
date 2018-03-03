import discord
from discord.ext import commands

class Simple():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def cool(self, ctx):
        await self.bot.send_message(ctx.message.channel, 'im cool 8-)')


def setup(bot):
    bot.add_cog(Simple(bot))
