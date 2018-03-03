import discord
from discord.ext import commands
import asyncio, json


"""
On reaction ADD-POST
db commit message ID, timestamp, author, upvoters

On reaction DEL-POST
db f

"""

class Curate_Web():
    def __init__(self, bot):
        self.bot = bot


    async def raw_reaction_handler(self, raw_msg):
        """
        Necessary to handle raw socket events in case of bot downtime. Reaction and deletion events for messages
         not in bot's Message queue will not be handled by the native event handlers.

         Need to construct and return enough context in discord.py's classes.

        :param raw_msg:
        :return:
        """
        if type(raw_msg) is str:
            raw_json = json.loads(raw_msg)
            try:
                server = list(self.bot.servers)[0]  # TODO: support multiple server instances for web curator bot?
                channel = server.get_channel(raw_json["d"]["channel_id"])
                message = await self.bot.get_message(channel, raw_json["d"]["message_id"])

                if raw_json["t"] == "MESSAGE_REACTION_ADD":
                    pass

                elif raw_json["t"] == "MESSAGE_REACTION_REMOVE":
                    pass

                elif raw_json["t"] == "MESSAGE_DELETE":
                    pass

            except (TypeError, KeyError):
                print(raw_json)

        else: print('raw bytes content')

    async def on_socket_raw_receive(self, msg):
        await self.raw_reaction_handler(msg)

    async def on_reaction_add(self, reaction, user):
        pass

    async def on_reaction_remove(self, reaction, user):
        pass 

def setup(bot):
    bot.add_cog(Curate_Web(bot))
