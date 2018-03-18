import discord
from discord.ext import commands
import json, os, sys
import traceback
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def namestr(obj, namespace):
    return [name for name in namespace if namespace[name] is obj]
    # usage example print(namestr(VAR_NAME, locals())[0] + '=' + VAR_NAME.property)


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
        print('entered ' + sys._getframe().f_code.co_name)
        async def get_msg_reaction_count(): pass #TODO: accurately represent the reaction count


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
        # print('entered ' + sys._getframe().f_code.co_name)

        if (handled_events is None) or (type(raw_msg) is not str):
            return

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

    # TODO: make a generic reaction filter -> cb engine, emojis can drive other apps
    async def on_socket_raw_receive(self, msg):
        #  >1 Server object exists (bot.is_logged in returns True before Server object exists!)
        if list(self.bot.servers):
            # Using raw_reaction_handler should be mutually exclusive with using the native
            # reaction event handlers of discord.py
            await self.raw_reaction_handler(
                msg,
                {
                    "MESSAGE_REACTION_ADD": self.cb_add_reaction,
                    # "MESSAGE_REACTION_REMOVE": self.web_del_post,
                }
            )


    async def cb_add_reaction(self, context):
        print('entered '+ sys._getframe().f_code.co_name)
        (channel, initiator_user, reaction) = context
        print("  emoji.id & emoji.name=" + str(reaction.emoji.id) + " " + reaction.emoji.name)
        try:
            # check for custom emoji id or name of built-in emoji matches
            if (reaction.emoji.id or reaction.emoji.name) in self.reaction_ids_add_post:
                print('found add_post reaction match')
                await self.bot.add_reaction(reaction.message, "🛠")

                db = self.bot.db
                # get_one_or_create() returns tuple of Query and Boolean
                # anyone who has channel permission to Send Message can have their content curated
                (author, author_existed) = db.models.get_one_or_create(self.db_session, db.models.Author, **{
                    'nickname':  reaction.message.author.name,
                    'discord_id': reaction.message.author.id
                    }
                )

                # TODO: curators need to be authorized users AND/OR not post to web unless >N curators have reacted
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

                if reaction.message.attachments != []:
                    article.attachment = reaction.message.attachments[0]["url"]

                self.db_session.add(author)
                self.db_session.add(curator)
                self.db_session.add(article)
                self.db_session.commit()
                await self.bot.send_message(reaction.message.author, "{} has curated your post in {}: {}".format(initiator_user.name, reaction.message.channel.name, reaction.message.content))
                await self.bot.send_typing(reaction.message.channel)
                await self.bot.add_reaction(reaction.message, "✅")


            # Delete Message
            elif (reaction.emoji.id or reaction.emoji.name) in self.reaction_ids_del_post:
                try:
                    print('found add_post reaction match')

                    db = self.bot.db
                    await self.bot.send_typing(reaction.message.channel)
                    await self.bot.add_reaction(reaction.message, "🛠")
                    # get_one_or_create() returns tuple of Query and Boolean
                    """
                    (author, author_existed) = db.models.get_one_or_create(self.db_session, db.models.Author, **{
                        'nickname':  reaction.message.author.name,
                        'discord_id': reaction.message.author.id
                        }
                    )
                    """
                    article = self.db_session.query(db.models.Article).filter_by(discord_msg_id=reaction.message.id).first()

                    if article is not None:
                        self.db_session.delete(article)
                        self.db_session.commit()

                        await self.bot.send_message(reaction.message.channel,"```\r\n {} deleted article written on {} by {}```".format(initiator_user.name, article.timestamp, reaction.message.author.name))
                        await self.bot.remove_reaction(reaction.message, "✅", self.bot.user)

                except Exception:
                    traceback.print_exc()

                finally:
                    await self.bot.remove_reaction(reaction.message, "🛠", self.bot.user)
            else:
                return

        except Exception:
            traceback.print_exc()
            return


    async def web_del_post(self, context):
        print('entered ' + sys._getframe().f_code.co_name)
        (channel, initiator_user, reaction) = context
        print("  emoji.id=" + str(reaction.emoji.id) + " " + reaction.emoji.name)


    #TODO: update Article database with post edits
    async def web_edit_post(self, context):
        pass


def setup(bot):
    bot.add_cog(Curate_Web(bot))
