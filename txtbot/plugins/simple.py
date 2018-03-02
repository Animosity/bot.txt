import discord
from discord.ext import commands

class Simple():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def cool(self, ctx):
        await self.bot.send_message(ctx.message.channel, 'im cool 8-)')

    @commands.command(pass_context=True)
    async def txt(self, ctx):
        await self.bot.send_message(ctx.message.channel, 'big surprise made it to 60 y/o again')

    @commands.command(pass_context=True)
    async def dad(self, ctx):
        await self.bot.send_message(ctx.message.channel, 'owned, get mad nerd trash kid you are my son')


def setup(bot):
    bot.add_cog(Simple(bot))
