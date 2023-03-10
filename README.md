# DiscordBot-EdgeGPT
> ### Using Bing on discord bot, your Microsoft account needs to be able to access Bing first.

## Features
* chat: `/chat [message]`

  ![edgegpt1](https://i.imgur.com/SLv6dpp.png)
  ![edgegpt2](https://i.imgur.com/cnJmY79.png)

* reset: `/reset`

  ![reset](https://i.imgur.com/Csst7Y3.png)

## Install
```
$ git clone https://github.com/FuseFairy/DiscordBot-EdgeGPT.git
$ cd DiscordBot-EdgeGPT
$ pip install -r requirements.txt
```

## Usage
1. Rename the file `.env.dev` to `.env`, then open it and edit it.
   ```
   DISCORD_BOT_TOKEN=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   ```
   
2. Get Bing authentication.
   * Install the cookie editor extension for Chrome or Firefox.
   * Go to [bing.com](http://bing.com/chat)
   * Click "Export" on the bottom right.
   * Paste your cookies into a file `cookies.json`

4. Start run your bot, hosted locally or on a server.

   -> Recommended Free Servers: [fly.io](https://fly.io/)

## Credits
* EdgeGPT - [https://github.com/acheong08/EdgeGPT](https://github.com/acheong08/EdgeGPT)
* other - [https://github.com/Zero6992/chatGPT-discord-bot](https://github.com/Zero6992/chatGPT-discord-bot)
