from discord.ext import commands
import sys, requests
from bs4 import BeautifulSoup
from pprint import pprint
import traceback


class Overwatch():
    def __init__(self, bot):
        self.bot = bot
        self.bnet_ids = ["reportwidow#1905", "reportwidow#1262", "User#1886", "sentrysteve#1915"]

    @commands.command(pass_context=True)
    async def sr(self, ctx):
        print('entered ' + sys._getframe().f_code.co_name)

        response_markdown = "```css\r\n"
        for id in self.bnet_ids:
            await self.bot.send_typing(ctx.message.channel)
            try:
                stats_url = 'https://playoverwatch.com/en-us/career/{platform}/{region}/{battle_tag}'
                stats_url = stats_url.format(platform='pc', region='us', battle_tag=id.replace('#', '-'))

                result = requests.get(stats_url)

                if result.status_code is 200:
                    soup = BeautifulSoup(result.content, "html.parser")
                    sr = soup.find('div', attrs={'class': 'u-align-center h5'})
                    if sr:
                        response_markdown += (id + " SR = " + sr.string + "\r\n")
                        #await self.bot.send_message(ctx.message.channel, id + ' SR = ' + sr.string)

                    else:
                        response_markdown += (id + " is still in placements\r\n")
                        #await self.bot.send_message(ctx.message.channel, id + ' is still in placements')

                else:

                    response_markdown += (id + " SR = *failed to get stats response*\r\n")
                    #await self.bot.send_message(ctx.message.channel, id + ' SR = *failed to get stats response*')

            except:
                traceback.print_exc()
                #await self.bot.send_message(ctx.message.channel, id + ' *failed to get stats response*')

        response_markdown += "```"
        await self.bot.send_message(ctx.message.channel, response_markdown)
        return

def setup(bot):
    bot.add_cog(Overwatch(bot))
