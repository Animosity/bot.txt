from discord.ext import commands
from discord import Game
import sys, requests
from bs4 import BeautifulSoup
from pprint import pprint
import traceback


class Overwatch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = self.bot.config["OVERWATCH"]
        self.bnet_ids = self.config["BNET_IDS"]
    
    def get_sr_by_role(self, soup):
        ratings = {"TANK": "0", "DAMAGE": "0", "SUPPORT": "0"}
    
        for role in soup:
            #print(role)
            tank_sr = role.find('div', attrs={'data-ow-tooltip-text': 'Tank Skill Rating'})
            if tank_sr: 
                ratings["TANK"] = role.find('div', attrs={'class': 'competitive-rank-level'}).string
            
            damage_sr = role.find('div', attrs={'data-ow-tooltip-text': 'Damage Skill Rating'})
            if damage_sr: 
                ratings["DAMAGE"] = role.find('div', attrs={'class': 'competitive-rank-level'}).string
            
            support_sr = role.find('div', attrs={'data-ow-tooltip-text': 'Support Skill Rating'})
            if support_sr:
                ratings["SUPPORT"] = role.find('div', attrs={'class': 'competitive-rank-level'}).string
            #print(f"{ratings}")
        return ratings
    
    @commands.command(pass_context=True)
    async def sr(self, ctx):
        print('entered ' + sys._getframe().f_code.co_name)
        activity = discord.Streaming(name='Overwatch League', url='https://www.twitch.tv/overwatchleague', type=1)
        await self.bot.change_presence(activity=activity)
        await ctx.message.add_reaction("🛠")

        response_markdown = "```\r\n"
        try:
            async with ctx.typing():
                for id in self.bnet_ids:
                    try:
                        stats_url = 'https://playoverwatch.com/en-us/career/{platform}/{battle_tag}'
                        stats_url = stats_url.format(platform='pc', battle_tag=id.replace('#', '-'))
                
                        result = requests.get(stats_url)
    
                        if result.status_code is 200:
                            soup = BeautifulSoup(result.content, "html.parser")
                            ratings = soup.find_all('div', attrs={'class': 'competitive-rank'})
                            if ratings:
                                sr_by_role = self.get_sr_by_role(ratings[0])
                            
                                response_markdown += (id + " T=" + sr_by_role["TANK"] + "/D=" + sr_by_role["DAMAGE"] + "/S=" + sr_by_role["SUPPORT"] +  "\r\n")
                            else:
                                response_markdown += (id + " is still in placements\r\n")
                
                        else:
                            response_markdown += (id + " SR = *failed to get stats response*\r\n")
                    except: 
                      traceback.print_exc()
        except:
            traceback.print_exc()

        finally:
            response_markdown += "```"

        await ctx.send(response_markdown)
        await self.bot.change_presence(activity=None)
        await ctx.message.remove_reaction("🛠", ctx.me)
        return

def setup(bot):
    bot.add_cog(Overwatch(bot))
