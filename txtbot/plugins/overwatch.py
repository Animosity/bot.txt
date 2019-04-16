import discord
from discord.ext import commands
import sys, requests
from bs4 import BeautifulSoup
from pprint import pprint
import traceback


class Overwatch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = self.bot.config["OVERWATCH"]
        self.bnet_ids = self.config["BNET_IDS"]

    @commands.command(pass_context=True)
    async def sr(self, ctx):
        print('entered ' + sys._getframe().f_code.co_name)
        activity = discord.Streaming(name='Overwatch League', url='https://www.twitch.tv/overwatchleague', type=1)
        await self.bot.change_presence(activity=activity)

        response_markdown = "```\r\n"
        for id in self.bnet_ids:
            async with ctx.typing():
                try:
                    stats_url = 'https://playoverwatch.com/en-us/career/{platform}/{battle_tag}'
                    stats_url = stats_url.format(platform='pc', battle_tag=id.replace('#', '-'))

                    result = requests.get(stats_url)

                    if result.status_code is 200:
                        soup = BeautifulSoup(result.content, "html.parser")
                        sr = soup.find('div', attrs={'class': 'u-align-center h5'})
                        if sr:
                            response_markdown += (id + " SR = " + sr.string + "\r\n")

                        else:
                            response_markdown += (id + " is still in placements\r\n")

                    else:
                        response_markdown += (id + " SR = *failed to get stats response*\r\n")

                except:
                    traceback.print_exc()

        response_markdown += "```"
        await ctx.send(response_markdown)
        await self.bot.change_presence(activity=None)
        return


def setup(bot):
    bot.add_cog(Overwatch(bot))
