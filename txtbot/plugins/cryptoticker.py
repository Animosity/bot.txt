from discord.ext import commands
import asyncio
import requests
import json

currency_symbol_dict = {'USD': '$', 'BTC': '₿', 'ETH': 'Ξ', 'LTC': 'Ł', 'EUR': '€', 'JPY': '¥', 'RUB': '₽',
                        'AED': 'د.إ', 'BDT': '৳', 'BHD': 'BD', 'CNY': '¥', 'CZK': 'Kč', 'DKK': 'kr.', 'GBP': '£',
                        'HUF': 'Ft', 'IDR': 'Rp', 'ILS': '₪', 'INR': '₹', 'KRW': '₩', 'KWD': 'KD', 'LKR': 'රු',
                        'MMK': 'K', 'MYR': 'RM', 'NOK': 'kr', 'PHP': '₱', 'PKR': 'Rs', 'PLN': 'zł', 'SAR': 'SR',
                        'SEK': 'kr', 'THB': '฿', 'TRY': '₺', 'VEF': 'Bs.', 'VND': '₫', 'ZAR': 'R', 'XDR': 'SDR',
                        'XAG': 'XAG', 'XAU': 'XAU'}


class CryptoTicker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = self.bot.config["CRYPTOTICKER"]

        self.base_currency = self.config["BASE_CURRENCY"]
        self.url = self.config["URL"]
        self.coin_list = requests.get(self.config["COIN_LIST"]).json()
        self.supported_currencies = requests.get(self.config["SUPPORTED_CURRENCIES"]).json()

        self.this_extension = 'plugins.cryptoticker'

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'newbase':
                await ctx.send(f'```BASE_CURRENCY: {self.base_currency}\n'
                               f'command usage: basecurrency <currency>```')
                print(f'[CryptoTicker Prompted]: {ctx.message.author}: basecurrency')
                print('[CryptoTicker Returned]: basecurrency usage message')

        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'ticker':
                await ctx.send('```command usage: price <currency> [base_currency]```')
                print(f'[CryptoTicker Prompted]: {ctx.message.author}: price')
                print('[CryptoTicker Returned]: price usage message')

    @commands.command(pass_context=True)
    async def basecurrency(self, ctx, newbase):
        print(f'[CryptoTicker Prompted]: {ctx.message.author}: basecurrency {newbase}')
        if newbase in self.supported_currencies:
            try:
                self.bot.config["CRYPTOTICKER"]["BASE_CURRENCY"] = newbase.lower()
                with open(self.bot.configpath, 'w') as updatedconfigfile:
                    json.dump(self.bot.config, updatedconfigfile, indent=2, sort_keys=False, ensure_ascii=False)

                self.bot.unload_extension(self.this_extension)
                self.bot.load_extension(self.this_extension)

                async with ctx.typing():
                    await asyncio.sleep(1)
                    await ctx.send(f'Changing default base currency to {newbase.upper()}')
                    print(f'[CryptoTicker Reload]: Config update - BASE_CURRENCY is now {newbase.upper()}')
                    await ctx.message.add_reaction('\N{THUMBS UP SIGN}')

            except Exception as error:
                async with ctx.typing():
                    await asyncio.sleep(1)
                    await ctx.send(f'basecurrency command returned with error: {error}')
                    print(f'[CryptoTicker Error]: basecurrency command returned with error: {error}')
                    await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')
        else:
            async with ctx.typing():
                await asyncio.sleep(1)
                await ctx.send(f'CryptoTicker Error: {newbase} is not a supported currency')
                print(f'[CryptoTicker Error]: {newbase} is not a supported currency')
                await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')

    @commands.command(pass_context=True)
    async def price(self, ctx, ticker, base=None):
        if base is None:
            base = self.base_currency

        print(f'[CryptoTicker Prompted]: {ctx.message.author}: price {ticker} {base}')

        currency_symbol = currency_symbol_dict.get(base.upper(), '$')

        ticker = ticker.lower()
        base = base.lower()

        if base in self.supported_currencies:
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
                    await ctx.send(symbol.upper() + '/' + base.upper() + ': ' + currency_symbol + str(formatted_price))
                    print(f'[CryptoTicker Returned]: {symbol.upper()}/{base.upper()}:'
                          f' {currency_symbol}{str(formatted_price)}')
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
                await ctx.send(f'CryptoTicker error: {base} is not a supported currency')
                print(f'[CryptoTicker Error]: User: {ctx.message.author} Error: {base} is not a supported currency')
                await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')


def setup(bot):
    bot.add_cog(CryptoTicker(bot))
