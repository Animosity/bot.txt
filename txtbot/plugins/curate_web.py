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

    async def get_emoji_class(self, server, json_emoji):
        """
        Adapt raw socket data's emoji dict to Discord.py Emoji class

        :param json_emoji:
        :return: discord.Emoji
        """
        print('entered ' + sys._getframe().f_code.co_name)
        try:
            emoji_obj = discord.Emoji(**{
                'server': server,
                "require_colons": True,
                "managed": False,
                "id": json_emoji["id"],
                "name": json_emoji["name"],
                "roles": None,
            })
            return emoji_obj
        except:
            traceback.print_exc()
            return None


    async def raw_reaction_handler(self, raw_msg, handled_events=None):
        print('entered ' + sys._getframe().f_code.co_name)
        """
        Necessary to handle raw socket events in case of bot downtime. Reaction and deletion events for messages
        not in bot's Message queue will not be handled by the native event handlers.

        This function will construct and return enough context (using discord.py's classes) to callback functions.

        :param raw_msg:
        :return function callback with reaction context
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
                    server = list(self.bot.servers)[0]  # TODO: support multiple server instances for web curator bot?
                    channel = server.get_channel(raw_json["d"]["channel_id"])
                    reaction_message = await self.bot.get_message(channel, raw_json["d"]["message_id"])
                    initiator_user = server.get_member(raw_json["d"]["user_id"])
                    json_emoji = raw_json["d"]["emoji"]
                    emoji = await self.get_emoji_class(server, json_emoji)
                    reaction_obj = None

                    print(namestr(initiator_user, locals())[0] + '=' + initiator_user.id)
                    context = (channel, reaction_message, initiator_user, emoji)
                    print(json.dumps(raw_json, sort_keys=True, indent=4))

                    return await handled_events[raw_json["t"]](context)

                else:
                    return

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
