from discord.ext import commands
import asyncio
import requests
import json


class CryptoTicker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = self.bot.config["CRYPTOTICKER"]
        self.bot.configpath = '../' + 'config.json'
        self.this_extension = ['plugins.cryptoticker']
        self.base_currency = self.config["BASE_CURRENCY"]
        self.url = self.config["URL"]
        self.coin_list = requests.get(self.config["COIN_LIST"]).json()
        self.supported_currencies = requests.get(self.config["SUPPORTED_CURRENCIES"]).json()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'newbase':
                await ctx.send('basecurrency usage: basecurrency <currency>')

        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'ticker':
                await ctx.send('price usage: price <currency> [base_currency]')

    @commands.command(pass_context=True)
    async def basecurrency(self, ctx, newbase):
        if newbase in self.supported_currencies:
            for cryptoticker in self.this_extension:
                try:
                    self.bot.config["CRYPTOTICKER"]["BASE_CURRENCY"] = newbase.lower()
                    with open(self.bot.configpath, 'w') as updatedconfigfile:
                        json.dump(self.bot.config, updatedconfigfile, indent=2, sort_keys=False, ensure_ascii=False)

                    self.bot.unload_extension(cryptoticker)
                    self.bot.load_extension(cryptoticker)

                    async with ctx.typing():
                        await asyncio.sleep(1)
                        await ctx.send(f'Changing default base currency to {newbase.upper()}')
                        print(f'[Reloading CryptoTicker] Config update: BASE_CURRENCY is now {newbase.upper()}')
                        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')

                except Exception as error:
                    async with ctx.typing():
                        await asyncio.sleep(1)
                        await ctx.send(f'basecurrency command returned with error: {error.tr}')
                        print(f'basecurrency command returned with error: {error}')
                        await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')
        else:
            async with ctx.typing():
                await asyncio.sleep(1)
                await ctx.send(f'CryptoTicker Error: {newbase} is not a supported currency')
                print(f'CryptoTicker Error: {newbase} is not a supported currency')
                await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')

    @commands.command(pass_context=True)
    async def price(self, ctx, ticker, base=None):
        ticker = ticker.lower()

        if base is None:
            base = self.base_currency

        base = base.lower()

        if ticker in self.supported_currencies and base in self.supported_currencies:
            try:
                for coin in self.coin_list:
                    if ticker == coin['symbol']:
                        ticker = coin['id']

                response = requests.get(self.url + ticker + '&vs_currency=' + base)
                fetched = response.json()
                symbol = fetched[0]['symbol']
                current_price = fetched[0]['current_price']
                formatted_price = '{0:,.4f}'.format(current_price)
                async with ctx.typing():
                    await asyncio.sleep(1)
                    await ctx.send(symbol.upper() + '/' + base.upper() + ': $' + str(formatted_price))
                    await ctx.message.add_reaction('\N{THUMBS UP SIGN}')

            except Exception as error:
                async with ctx.typing():
                    await asyncio.sleep(1)
                    await ctx.send(f'price command returned with error: {error}')
                    print(f'price command returned with error: {error}')
                    await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')

        else:
            async with ctx.typing():
                await asyncio.sleep(1)
                await ctx.send(f'{ticker} or {base} is not a supported currency')
                await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')


def setup(bot):
    bot.add_cog(CryptoTicker(bot))