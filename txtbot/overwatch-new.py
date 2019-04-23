import discord
from discord.ext import commands
import sys
import requests


class Overwatch2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = self.bot.config["OVERWATCH"]
        self.bnet_ids = self.config["BNET_IDS"]

    @commands.command(pass_context=True)
    async def sr2(self, ctx):
        print('entered ' + sys._getframe().f_code.co_name)
        activity = discord.Streaming(name='Overwatch League', url='https://www.twitch.tv/overwatchleague', type=1)
        await self.bot.change_presence(activity=activity)

        response_markdown = "```\r\n"
        for tag in self.bnet_ids:
            async with ctx.typing():
                try:
                    stats_url = 'https://ow-api.com/v1/stats/pc/usa/{battle_tag}/profile'
                    stats_url = stats_url.format(battle_tag=tag.replace('#', '-'))

                    result = requests.get(stats_url)
                    data = result.json()
                    sr = data['rating']
                    if sr:
                        response_markdown += (tag + " SR = " + str(sr) + "\r\n")

                    else:
                        response_markdown += (tag + " is in placements or private profile\r\n")

                except Exception as error:
                    print(error)

        response_markdown += "```"
        await ctx.send(response_markdown)
        await self.bot.change_presence(activity=None)
        return


def setup(bot):
    bot.add_cog(Overwatch2(bot))
