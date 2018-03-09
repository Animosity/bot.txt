import discord
from discord.ext import commands
import argparse, os, json, logging, traceback, sys
from os import listdir
from os.path import isfile, join

sys.path.append("..")
from txtweb import db

print(db)
PATH_PLUGINDIR = "plugins"

bot = commands.Bot(command_prefix="!")


@bot.event
async def on_ready():
    print('logged in as '+ bot.user.name)


if __name__ == '__main__':
    logging.basicConfig(filename='txtbot.log', level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument('-dt', '--discord-token', help='Discord Bot Token')
    parser.add_argument('-k', '--keyfile', help='Relative path to keys.json', default='keys.json')
    args = vars(parser.parse_args())

    try:
        token = os.environ["DISCORD_TOKEN"]

    except KeyError:
        try:
            if args['keyfile']:
                token = json.load(open('../' + args['keyfile']))["DISCORD_TOKEN"]

        except(KeyError, FileNotFoundError):
            logging.info('error loading DISCORD_TOKEN from keyfile')

    for plugin in [f.replace('.py', '') for f in listdir(PATH_PLUGINDIR) if isfile(join(PATH_PLUGINDIR, f))]:
        try:
            bot.load_extension(PATH_PLUGINDIR + "." + plugin)
            print(f'Loading plugin: {plugin}...')

        except Exception as e:
            print(f'Failed to load plugin: {plugin}.')
            traceback.print_exc()


    bot.run(token)