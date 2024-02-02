# DiscordBot-EdgeGPT
## Using Microsoft's Bing Chat AI and Bing Image Creator on discord bot.

![demo](https://i.imgur.com/mvg18xh.gif)

## Update
> ### 2024/2/2：To optimize usage, recommended to re-read the README.
> ### 2024/1/27：Add jail break version, but image uploads are currently not supported, and python version need 3.10+.
> ### 2024/1/15：Can create thread to chat with Copilot.
> ### 2023/12/22：Support uploading image while chatting.
   
## Features

<details>
   <summary>
   
   ### Slash command

   </summary>
   
> ### will create a separate chat for each user.
   
* cookies setting(can use personal Bing Cookies): `/cookies setting [cookies_file] [auth_cookie]`
  * Can upload own cookies (get from https://copilot.microsoft.com/) or auth_cookie (get from https://bing.com/, and copy the value from the _U). Supports simultaneous uploads.
  ![setting](https://i.imgur.com/Smca2HO.png)
  
* copilot: `/copilot [version] [style] [type]`
  * A separate thread will be created.
    * [version]：`default` can chat with Copilot, `jailbreak` chat with Sydney, but `jailbreak` image uploads are not currently supported.
    * [style]：Have 3 conversation style can choose, `creative`、`balanced` and `precise`.
    * [type]：Options for thread type, `public` or `private`.

  ![copilot](https://i.imgur.com/ctcGb7I.png)
  
* bing image creator: `/create image [prompt]`
  
  ![bingimage.png](https://i.imgur.com/pSCI1bg.png)

* reset conversation: `/reset conversation`

  ![reset](https://i.imgur.com/7CyEFao.png)
</details>

<details>
   <summary>
   
   ### Mention bot

   </summary>

> ### same function as the slash command, but this will reply all user messages.

* If only the bot is mentioned, you will get a drop-down list of settings.

  ![dropdown1](https://i.imgur.com/XDcnTuC.png)
  ![dropdown2](https://i.imgur.com/azHIUqv.png)

* Same as use `/bing`,

  ![mention1](https://i.imgur.com/BDy0See.png)

</details>

<details>
   <summary>
   
   ### Prefix command (available only to bot owner)

   </summary>
 
 > ### bot owner setting.
   
 * `!unload [file_name_in_cogs_folder]`: Disable command from the specified file.
 * `!load [file_name_in_cogs_folder]`: Enable the command from the specified file.
 
   ![load & unload](https://i.imgur.com/spsyAEG.png)
  
 * `!clean`: Empty discord_bot.log file.
 * `!getLog`: Get discord_bot.log file. Real-time tracking of the bot's operating status.
   
   ![getLog](https://i.imgur.com/LHX4yWV.png)
 
 * `!upload [.txt_file]`: Same as `/cookies setting`, but for default cookies and auth_cookie.
 
   ![upload](https://i.imgur.com/clvPcIM.png)
</details>

## Install
```
pip install -r requirements.txt
```

## Usage
1. Rename the file`.env.dev`to`.env`, then open it and edit it.
   ```env
   DISCORD_BOT_TOKEN="input your Dicord bot token"
   IMAGE_TIMEOUT=300
   IMAGE_MAX_CREATE_SEC=300

   # Get from https://bing.com/, and copy the value from the _U, not necessary to set.
   AUTH_COOKIE=

   # Allow mention bot only in specific channel, if you don't set it, just default to all channels.
   MENTION_CHANNEL_ID=

   # Allow each commands only in specific channel, if you don't set it, just default to all channels.
   # specific channel for /cookies setting
   SETTING_CHANNEL_ID=

   # specific channel for /copilot
   CHAT_CHANNEL_ID=

   # specific channel for /create image
   CREATE_IMAGE_CHANNEL_ID=

   # specific channel for /reset conversation
   RESET_CHAT_CHANNEL_ID=

   # specific channel for /help
   HELP_CMD_CHANNEL_ID=
   ```
   
2. It is not necessary to create the `cookies.json` file, but if you do, there will be more conversation.
   * Install the cookie editor extension for Chrome or Firefox.
   * Go to [copilot.microsoft.com](https://copilot.microsoft.com/)
   * Click "Export" on the bottom right.
   * Paste your cookies into a file `cookies.json`

4. Start run your bot, hosted locally or on a server.

   -> Recommended Free Servers: [fly.io](https://fly.io/)

## Credits
* ReEdgeGPT - https://github.com/Integration-Automation/ReEdgeGPT

* Sydney  - https://github.com/juzeon/SydneyQt/tree/v1

## Contributors

This project exists thanks to all the people who contribute.

[![](https://contrib.rocks/image?repo=FuseFairy/DiscordBot-EdgeGPT)](https://github.com/FuseFairy/DiscordBot-EdgeGPT/graphs/contributors)


## Star History
[![Star History Chart](https://api.star-history.com/svg?repos=FuseFairy/DiscordBot-EdgeGPT&type=Date)](https://star-history.com/#FuseFairy/DiscordBot-EdgeGPT&Date)
