import discord
from discord.ext import commands
import os, json, logging, traceback
from os import listdir
from os.path import isfile, join

PATH_PLUGINDIR = "plugins"

bot = commands.Bot(command_prefix="!")


@bot.event
async def on_ready():
    print('logged in as '+ bot.user.name)


if __name__ == '__main__':
    logging.basicConfig(filename='txtbot.log', level=logging.INFO)
    try:
        print("DISCORD_TOKEN" in os.environ)
        token = os.environ["DISCORD_TOKEN"]

    except KeyError:
        try:
            token = json.load(open('../mykeys.json'))["DISCORD_TOKEN"]
        except(KeyError, FileNotFoundError):
            logging.info('error loading DISCORD_TOKEN from../keys.json')

    for plugin in [f.replace('.py', '') for f in listdir(PATH_PLUGINDIR) if isfile(join(PATH_PLUGINDIR, f))]:
        try:
            bot.load_extension(PATH_PLUGINDIR + "." + plugin)
            print(f'Loading plugin {plugin}...')
        except Exception as e:
            print(f'Failed to load plugin {plugin}.')
            traceback.print_exc()


    bot.run(token)