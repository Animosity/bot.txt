# bot.txt
![notepad](https://i.imgur.com/7hEVKCs.png)

.txt  community website (www.dottxt.com) content management via Discord

## What: 
This project was started as a novel Discord server bot (backend: [discord.py](https://github.com/Rapptz/discord.py)) to perform web content curation thru Discord Reactions (emojis) applied to chat messages.

## How: 
In order to accomplish this, I wrote a [complete replacement](https://github.com/Animosity/bot.txt/blob/master/txtbot/plugins/curate_web.py#L81) of discord.py's native Reaction event handlers for robustness.

It was necessary due to a specific limitation in discord.py: Reactions upon messages which the bot instance did not witness, are not recognized by its native event handler. For programmers who are using Heroku or similar service which may suspend their processes, this is not satisfactory for the purpose of curating web content based upon chat _history_.

To solve this, the raw socket event handler is used to parse the Reaction events and yield discord.py context with the relevant Classes and these events are relayed to any designated callback functions to perform tasks.

Basic feedback is returned to the user in the form of additional Reactions applied to the message (in this case, the message being curated for the website). For example a 🛠 Reaction is added to message when the bot recognizes a supported Reaction/emoji has been added/removed to a chat message by the user. When the associated task is completed, the 🛠 Reaction is then removed from the message.

When a task is _successfully_ completed (such as adding a new web post), a ✅ Reaction is applied to the associated message by the bot.

A basic microblog is implemented in Flask to retrieve and render the curated web content from a PostgreSQL database which is populated with the curated content, from the server bot.



# TODO:
* [project kanban](https://github.com/Animosity/bot.txt/projects/1)
