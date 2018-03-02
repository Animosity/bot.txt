import discord
from discord.ext import commands
import os, json, logging
bot = commands.Bot(command_prefix="!")


@bot.event
async def on_ready():
    print('logged in as '+ bot.user.name)

@bot.command(pass_context=True)
async def cool(ctx):
    await bot.send_message(ctx.message.channel, 'im cool 8-)')

@bot.command(pass_context=True)
async def txt(ctx):
    await bot.send_message(ctx.message.channel, 'big surprise made it to 60 y/o again')

if __name__ == '__main__':
    logging.basicConfig(filename='txtbot.log', level=logging.DEBUG)
    try:
        token = os.environ["DISCORD_TOKEN"]
    except KeyError:
        try:
            token = json.load(open('../keys.json'))["DISCORD_TOKEN"]
        except(KeyError, FileNotFoundError):
            logging.info('error loading DISCORD_TOKEN from../keys.json')
    bot.run(token)