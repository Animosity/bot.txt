from discord.ext import commands
import asyncio
import requests
import json

configfile = '../' + 'config.json'
data = json.load(open(configfile))
base_currency = data["CRYPTOTICKER"]["BASE_CURRENCY"]
url = data["CRYPTOTICKER"]["URL"]

coin_list_url = data["CRYPTOTICKER"]["COIN_LIST"]
coin_fetch = requests.get(coin_list_url)
coin_list = coin_fetch.json()

supported_currencies_url = data["CRYPTOTICKER"]["SUPPORTED_CURRENCIES"]
supported_currencies_fetch = requests.get(supported_currencies_url)
supported_currencies_list = supported_currencies_fetch.json()

this_extension = ['plugins.cryptoticker']


class CryptoTicker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
        if newbase in supported_currencies_list:
            for cryptoticker in this_extension:
                try:
                    data["CRYPTOTICKER"]["BASE_CURRENCY"] = newbase.lower()
                    with open(configfile, 'w') as updatedconfigfile:
                        json.dump(data, updatedconfigfile, indent=2, sort_keys=False, ensure_ascii=False)

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
                        await ctx.send(f'basecurrency command returned with error: {error}')
                        print(f'basecurrency command returned with error: {error}')
                        await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')
        else:
            async with ctx.typing():
                await asyncio.sleep(1)
                await ctx.send(f'CryptoTicker Error: {newbase} is not a supported currency')
                print(f'CryptoTicker Error: {newbase} is not a supported currency')
                await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')

    @commands.command(pass_context=True)
    async def price(self, ctx, ticker, base: str = base_currency):
        ticker = ticker.lower()
        try:
            for coin in coin_list:
                if ticker == coin['symbol']:
                    ticker = coin['id']

            response = requests.get(url + ticker + '&vs_currency=' + base)
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


def setup(bot):
    bot.add_cog(CryptoTicker(bot))
