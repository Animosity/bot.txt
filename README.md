# bot.txt
![notepad](https://i.imgur.com/7hEVKCs.png)

.txt  community website (www.dottxt.com) content management via Discord

## What: 
This project was started as a novel Discord server bot (backend: [discord.py](https://github.com/Rapptz/discord.py)) to perform web content curation thru Discord Reactions (emojis) applied to chat messages.

Originally, this required custom implementation of raw reaction event handlers. 
However the rewrite of discord.py includes native raw Reaction event handlers which simplified this project's code greatly.

A basic microblog is implemented in Flask to retrieve and render the curated web content from a PostgreSQL database which is populated with the curated content, from the server bot.

