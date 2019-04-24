import random
from bs4 import BeautifulSoup
from discord.ext import commands

CLANCY_FILES = ['index_split_001','index_split_002','index_split_003','index_split_004', 'index_split_005','index_split_006','index_split_007','index_split_008', 'index_split_009', 'index_split_010', 'index_split_011']


class Clancy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def fetch_line(self):
        file = random.choice(CLANCY_FILES) + ".xhtml"

        try:
            with open(f".//plugins//resources//clancybot//{file}",'r') as handle:
                data = handle.read()
                soup = BeautifulSoup(data)

                lines = soup.select('span[class="none2"]')
                line = random.choice(lines).get_text()
                return f"*{line}*"

        except FileNotFoundError:
            return f"`Service administrators must provide own compatible Clancy files for use with this plugin.`"


    @commands.command(pass_context=True)
    async def clancy(self, ctx):
        async with ctx.typing():
            response = await self.fetch_line()
            await ctx.send(response)

def setup(bot):
    bot.add_cog(Clancy(bot))
