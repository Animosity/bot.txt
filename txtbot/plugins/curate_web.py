import discord
from discord.ext import commands
import json, os, sys
import traceback
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def namestr(obj, namespace):
    return [name for name in namespace if namespace[name] is obj]
    # usage example print(namestr(VAR_NAME, locals())[0] + '=' + VAR_NAME.property)


class Curate_Web(commands.Cog):
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

        self.bot.add_listener(self.on_raw_reaction_add, 'on_raw_reaction_add')

    async def get_reaction_class(self, message, emoji):
        """
        Adapt raw socket data data to Discord.py Reaction class
        :param message: discord.Message object
        :param emoji: discord.Emoji object
        :return discord.Reaction object
        """
        print('entered ' + sys._getframe().f_code.co_name)

        async def get_msg_reaction_count():
            pass  # TODO: accurately represent the reaction count

        try:
            reaction_obj = discord.Reaction(
                message=message,
                emoji=emoji,
                data={"count": 1, "me": False}
            )
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

    async def raw_reaction_handler(self, payload, handled_events):
        """
        The discord.py rewrite includes raw reaction event handlers now... so this function is rewritten for
        with previous curate_web.py code.

        :param raw_msg: the raw socket event data from on_socket_raw_receive()
        :param handled_event: event callback function

        :return the function callback with tuple parameter:
            e.g. context = (Discord.Message, Discord.User, Discord.Reaction)

        """
        # print('entered ' + sys._getframe().f_code.co_name)
        print('entered ' + sys._getframe().f_code.co_name)
        if (handled_events is None) or (type(payload) is not discord.RawReactionActionEvent):
            return

        try:
            server = list(self.bot.guilds)[0]  # TODO: support multiple server instances for web curator bot?
            channel = server.get_channel(payload.channel_id)
            reaction_message = await channel.fetch_message(payload.message_id)
            initiator_user = server.get_member(payload.user_id)
            # json_emoji = json_raw["d"]["emoji"]
            # emoji = await self.get_emoji_class(server, json_emoji)
            emoji = payload.emoji
            reaction = await self.get_reaction_class(reaction_message, emoji)
            print(reaction)
            context = (channel, initiator_user, reaction)

            return await handled_events(context)

        except (Exception):
            traceback.print_exc()
            return

    # TODO: make a generic reaction filter -> cb engine, emojis can drive other apps
    async def on_raw_reaction_add(self, payload):
        print('entered ' + sys._getframe().f_code.co_name)
        #  >1 Server object exists (bot.is_logged in returns True before Server object exists!)

        # Using raw_reaction_handler should be mutually exclusive with using the native
        # reaction event handlers of discord.py
        await self.raw_reaction_handler(
            payload,
            self.cb_add_reaction
        )

    async def cb_add_reaction(self, context):
        print('entered ' + sys._getframe().f_code.co_name)
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
                    'nickname': reaction.message.author.name,
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
                await self.bot.send_message(reaction.message.author,
                                            "{} has curated your post in {}: {}".format(initiator_user.name,
                                                                                        reaction.message.channel.name,
                                                                                        reaction.message.content))
                ctx = await self.bot.get_context(reaction.message)
                async with ctx.typing():
                    await reaction.message.add_reaction("✅")


            # Delete Message
            elif (reaction.emoji.id or reaction.emoji.name) in self.reaction_ids_del_post:
                try:
                    print('found del_post reaction match')

                    db = self.bot.db
                    ctx = await self.bot.get_context(reaction.message)
                    async with ctx.typing():
                        await reaction.message.add_reaction("🛠")
                    # await self.bot.send_typing(reaction.message.channel)
                    # await self.bot.add_reaction(reaction.message, "🛠")

                    # get_one_or_create() returns tuple of Query and Boolean
                    """
                    (author, author_existed) = db.models.get_one_or_create(self.db_session, db.models.Author, **{
                        'nickname':  reaction.message.author.name,
                        'discord_id': reaction.message.author.id
                        }
                    )
                    """
                    article = self.db_session.query(db.models.Article).filter_by(
                        discord_msg_id=reaction.message.id).first()

                    if article is not None:
                        self.db_session.delete(article)
                        self.db_session.commit()

                        await self.bot.send_message(reaction.message.channel,
                                                    "```\r\n {} deleted article written on {} by {}```".format(
                                                        initiator_user.name, article.timestamp,
                                                        reaction.message.author.name))
                        await reaction.message.remove_reaction("✅", self.bot.user)

                except Exception:
                    traceback.print_exc()

                finally:
                    await reaction.message.remove_reaction("🛠", self.bot.user)
            else:
                return

        except Exception:
            traceback.print_exc()
            return

        finally:
            await reaction.message.remove_reaction("🛠", self.bot.user)

    async def web_del_post(self, context):
        print('entered ' + sys._getframe().f_code.co_name)
        (channel, initiator_user, reaction) = context
        print("  emoji.id=" + str(reaction.emoji.id) + " " + reaction.emoji.name)

    # TODO: update Article database with post edits
    async def web_edit_post(self, context):
        pass


def setup(bot):
    bot.add_cog(Curate_Web(bot))