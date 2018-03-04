import discord
from discord.ext import commands
import json, sys
import traceback


"""
On reaction ADD-POST
db commit message ID, timestamp, author, upvoters

On reaction DEL-POST
db f

"""


def namestr(obj, namespace):
    return [name for name in namespace if namespace[name] is obj]

class Curate_Web():
    def __init__(self, bot):
        self.bot = bot


    async def raw_reaction_handler(self, raw_msg):
        print('entered ' + sys._getframe().f_code.co_name)
        """
        Necessary to handle raw socket events in case of bot downtime. Reaction and deletion events for messages
         not in bot's Message queue will not be handled by the native event handlers.

         Need to construct and return enough context in discord.py's classes.

        :param raw_msg:
        :return:
        """
        if type(raw_msg) is str:
            raw_json = json.loads(raw_msg)
            if not raw_json["t"]:
                return
            try:
                handled_events = {
                    "MESSAGE_REACTION_ADD": self.web_add_post,
                    "MESSAGE_REACTION_REMOVE": self.web_del_post,
                }

                if raw_json["t"] in handled_events:
                    print(json.dumps(raw_json, sort_keys=True, indent=4))

                    server = list(self.bot.servers)[0]  # TODO: support multiple server instances for web curator bot?
                    channel = server.get_channel(raw_json["d"]["channel_id"])
                    reaction_message = await self.bot.get_message(channel, raw_json["d"]["message_id"])
                    initiator_user = server.get_member(raw_json["d"]["user_id"])
                    d_emoji = raw_json["d"]["emoji"]
                    print(namestr(initiator_user, locals())[0] + '=' + initiator_user.id)
                    context = (channel, reaction_message, initiator_user, d_emoji)

                    return await handled_events[raw_json["t"]](context)

                else:
                    return
                #  << Stone Age >>
                """
                
                if raw_json["t"] == "MESSAGE_REACTION_ADD": 
                    print(raw_json)

                elif raw_json["t"] == "MESSAGE_REACTION_REMOVE": 
                    print(raw_json)

                elif raw_json["t"] == "MESSAGE_DELETE": web_edit_post
                    print(raw_json)
                """

            except (Exception):
                traceback.print_exc()
                print(json.dumps(raw_json, sort_keys=True, indent=4))
                return

        else:
            return

    async def on_socket_raw_receive(self, msg):
        if list(self.bot.servers): #  >1 Server object exists (bot.is_logged in returns True before Server object exists!)
            await self.raw_reaction_handler(msg)

    async def on_reaction_add(self, reaction, user):
        pass

    async def on_reaction_remove(self, reaction, user):
        pass

    async def on_reaction_remove(self, reaction, user):
        pass

    async def web_add_post(self, context):
        print('entered '+ sys._getframe().f_code.co_name)
        print(str(context))

    async def web_del_post(self, context):
        print('entered ' + sys._getframe().f_code.co_name)
        print(str(context))
    async def web_edit_post(self, context):
        pass

def setup(bot):
    bot.add_cog(Curate_Web(bot))
