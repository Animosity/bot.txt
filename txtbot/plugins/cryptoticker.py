from discord.ext import commands
import asyncio
import requests
import json

configfile = '../' + 'config.json'
data = json.load(open(configfile))
default_fiat = data["CRYPTOTICKER"]["DEFAULT_FIAT"]
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
            if error.param.name == 'newfiat':
                await ctx.send('setfiat usage: !setfiat <fiat>')

        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'ticker':
                await ctx.send('price usage: !price <currency> [fiat]')

    @commands.command(pass_context=True)
    async def setfiat(self, ctx, newfiat):
        if newfiat in supported_currencies_list:
            for cryptoticker in this_extension:
                try:
                    data["CRYPTOTICKER"]["DEFAULT_FIAT"] = newfiat.lower()
                    with open(configfile, 'w') as updatedconfigfile:
                        json.dump(data, updatedconfigfile, indent=2, sort_keys=False, ensure_ascii=False)

                    self.bot.unload_extension(cryptoticker)
                    self.bot.load_extension(cryptoticker)

                    async with ctx.typing():
                        await asyncio.sleep(1)
                        await ctx.send('Changing default fiat currency to ' + newfiat.upper())
                        print(f'[Reloading extension: CryptoTicker] Config update: default_fiat is now ' + newfiat.upper())
                        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')

                except Exception as error:
                    async with ctx.typing():
                        await asyncio.sleep(1)
                        await ctx.send(f'setfiat command returned with error: {error}')
                        print(f'setfiat command returned with error: {error}')
                        await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')
        else:
            async with ctx.typing():
                await asyncio.sleep(1)
                await ctx.send(f'CryptoTicker Error: {newfiat} is not a supported currency')
                print(f'CryptoTicker Error: {newfiat} is not a supported currency')
                await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')

    @commands.command(pass_context=True)
    async def price(self, ctx, ticker, fiat: str = default_fiat):
        ticker = ticker.lower()
        try:
            for coin in coin_list:
                if ticker == coin['symbol']:
                    ticker = coin['id']

            response = requests.get(url + ticker + '&vs_currency=' + default_fiat)
            fetched = response.json()
            symbol = fetched[0]['symbol']
            current_price = fetched[0]['current_price']
            formatted_price = '{0:,.4f}'.format(current_price)
            async with ctx.typing():
                await asyncio.sleep(1)
                await ctx.send(symbol.upper() + '/' + fiat.upper() + ': $' + str(formatted_price))
                await ctx.message.add_reaction('\N{THUMBS UP SIGN}')

        except Exception as error:
            async with ctx.typing():
                await asyncio.sleep(1)
                await ctx.send(f'price command returned with error: {error}')
                print(f'price command returned with error: {error}')
                await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')


def setup(bot):
    bot.add_cog(CryptoTicker(bot))
