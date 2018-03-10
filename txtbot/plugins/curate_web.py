import discord
from discord.ext import commands
import json, os, sys
import traceback
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


"""
On reaction ADD-POST
db commit message ID, timestamp, author, upvoters

On reaction DEL-POST
db f

"""

def namestr(obj, namespace):
    return [name for name in namespace if namespace[name] is obj]
    #usage example print(namestr(VAR_NAME, locals())[0] + '=' + VAR_NAME.property)


class Curate_Web():
    def __init__(self, bot):
        self.bot = bot
        self.config = self.bot.config["CURATE_WEB"]
        # DB session init
        Session = sessionmaker()
        engine = create_engine(os.environ['DATABASE_URL'])
        Session.configure(bind=engine)
        self.db_session = Session()
        # Fetch plugin settings
        self.reaction_ids_add_post = self.config["REACTION_IDS_ADD_POST"]
        self.reaction_ids_del_post = self.config["REACTION_IDS_DEL_POST"]


    async def get_reaction_class(self, message, emoji):
        """
        Adapt raw socket data data to Discord.py Reaction class
        :param message: discord.Message object
        :param emoji: discord.Emoji object
        :return discord.Reaction object
        """
        async def get_msg_reaction_count(): pass #TODO: accurately represent the reaction count

        print('entered ' + sys._getframe().f_code.co_name)
        try:
            reaction_obj = discord.Reaction(**{
                'emoji': emoji,
                "custom_emoji": False,
                "count": 1,
                "me": False,
                "message": message,
            })
            return reaction_obj

        except:
            traceback.print_exc()
            return None

    async def get_emoji_class(self, server, json_emoji):
        """
        Adapt raw socket data's emoji dict to Discord.py Emoji class

        :param server: discord.Server instance associated with the reaction event
        :param json_emoji: the 'd" dictionary from the raw socket event json

        :return: discord.Emoji object
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


    async def raw_reaction_handler(self, raw_msg, handled_events):
        #print('entered ' + sys._getframe().f_code.co_name)
        if (handled_events is None) or (type(raw_msg) is not str):
            return

        """
        Necessary to handle raw socket events in case of bot downtime. Reaction and deletion events for messages
        not in bot's Message queue will not be handled by the native event handlers.

        This function will construct and return enough context (using discord.py's classes) to callback functions.

        :param raw_msg: the raw socket event data from on_socket_raw_receive()
        :param handled_events: 
            dict with k->v mapping of: Discord reaction eventtype string -> event callback function
               e.g.  handled_events = {
                    "MESSAGE_REACTION_ADD": self.cb_reaction_add,
                    "MESSAGE_REACTION_REMOVE": self.cb_reaction_remove,
                }
                                
        :return the function callback with tuple parameter: 
            e.g. context = (Discord.Message, Discord.User, Discord.Reaction)
                        
        """

        json_raw = json.loads(raw_msg)
        if not json_raw["t"]:
            return

        try:
            if json_raw["t"] in handled_events:
                server = list(self.bot.servers)[0]  # TODO: support multiple server instances for web curator bot?
                channel = server.get_channel(json_raw["d"]["channel_id"])
                reaction_message = await self.bot.get_message(channel, json_raw["d"]["message_id"])
                initiator_user = server.get_member(json_raw["d"]["user_id"])
                json_emoji = json_raw["d"]["emoji"]
                emoji = await self.get_emoji_class(server, json_emoji)
                reaction = await self.get_reaction_class(reaction_message, emoji)

                context = (channel, initiator_user, reaction)

                return await handled_events[json_raw["t"]](context)

            else:
                return

        except (Exception):
            traceback.print_exc()
            print(json.dumps(json_raw, sort_keys=True, indent=4))
            return


    async def on_socket_raw_receive(self, msg):

        if list(self.bot.servers): #  >1 Server object exists (bot.is_logged in returns True before Server object exists!)
            await self.raw_reaction_handler(
                msg,
                {
                    "MESSAGE_REACTION_ADD": self.web_add_post,
                    "MESSAGE_REACTION_REMOVE": self.web_del_post,
                }
            )


    async def on_reaction_add(self, reaction, user):
        pass

    async def on_reaction_remove(self, reaction, user):
        pass

    async def on_reaction_remove(self, reaction, user):
        pass

    async def web_add_post(self, context):
        print('entered '+ sys._getframe().f_code.co_name)
        (channel, initiator_user, reaction) = context
        print(str(reaction.emoji.id) + " " + reaction.emoji.name)

        if reaction.emoji.id in self.reaction_ids_add_post:
            print('found add_post reaction match')

            db = self.bot.db
            # get_one_or_create() returns tuple of Query and Boolean
            # anyone who has channel permission to Send Message can have their content curated
            (author, author_existed) = db.models.get_one_or_create(self.db_session, db.models.Author, **{
                'nickname':  reaction.message.author.name,
                'discord_id': reaction.message.author.id
                }
            )

            # TODO: curators need to be authorized users OR not post to web unless >N curators have reacted
            (curator, curator_existed) = db.models.get_one_or_create(self.db_session, db.models.Curator, **{
                'nickname': initiator_user.name,
                'discord_id': initiator_user.id
            }
                                                                                                   )
            (article, article_existed) = db.models.get_one_or_create(self.db_session, db.models.Article, **{
                'discord_msg_id': reaction.message.id,
                'content_markdown': reaction.message.content,
                'author_id': author.id,  # the Author model primary key from
                'timestamp': reaction.message.timestamp,
                'curator_id': curator.id  # the Curator model primary key
                }
            )

            self.db_session.add(author)
            self.db_session.add(article)
            self.db_session.add(curator)
            self.db_session.commit()

            #if not db.models.Author.query.filter(discord_id=)
            #article = db.models.Article()

    async def web_del_post(self, context):
        print('entered ' + sys._getframe().f_code.co_name)
        (channel, initiator_user, reaction) = context
        print(reaction.emoji.id)

    async def web_edit_post(self, context):
        pass

def setup(bot):
    bot.add_cog(Curate_Web(bot))
