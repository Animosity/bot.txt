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

    async def sr_fallback(self, ctx):
        print('entered ' + sys._getframe().f_code.co_name)
        response_markdown = ""
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
                            response_markdown += (id + " is in placements or private profile\r\n")

                    else:
                        response_markdown += (id + " SR = *failed to get stats response*\r\n")

                except:
                    traceback.print_exc()
                    await ctx.send("Error fetching from web scraper")


        return response_markdown


    @commands.command(pass_context=True)
    async def sr(self, ctx):
        print('entered ' + sys._getframe().f_code.co_name)
        activity = discord.Streaming(name='Overwatch League', url='https://www.twitch.tv/overwatchleague', type=1)
        await self.bot.change_presence(activity=activity)
        await ctx.message.add_reaction("🛠")

        response_markdown = "```\r\n"
        try:
            async with ctx.typing():
                for tag in self.bnet_ids:
                        stats_url = 'https://ow-api.com/v1/stats/pc/usa/{battle_tag}/profile5'
                        stats_url = stats_url.format(battle_tag=tag.replace('#', '-'))

                        result = requests.get(stats_url)
                        data = result.json()
                        sr = data['rating']
                        if sr:
                            response_markdown += (tag + " SR = " + str(sr) + "\r\n")

                        else:
                            response_markdown += (tag + " is in placements or private profile\r\n")
        except:
            traceback.print_exc()
            await ctx.send("Error fetching from API, trying web scraper")
            response_markdown = "```\r\n"
            response_markdown += await self.sr_fallback(ctx)

        finally:
            response_markdown += "```"

        await ctx.send(response_markdown)
        await self.bot.change_presence(activity=None)
        await ctx.message.remove_reaction("🛠")
        return


def setup(bot):
    bot.add_cog(Overwatch(bot))
