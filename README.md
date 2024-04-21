# DiscordBot-EdgeGPT

  <a href="https://www.python.org/downloads/">
    <img alt="PyPI - Python Version" src="https://img.shields.io/badge/pyversion-3.10%2B-blue?style=flat&label=python">
  </a>

  [![Try with Replit Badge](https://replit.com/badge?caption=Try%20with%20Replit)](https://replit.com/@dd8611706/DiscordBot-EdgeGPT?v=1)



## Update
> ### 2024/4/21：Supporting the Suno plugin with Copilot.
> ### 2024/3/30：Support DALLE-3(Unofficial), get api key from https://dalle.feiyuyu.net/dashboard.
> ### 2024/3/5：Images can be generated while chatting.
> ### 2024/2/2：To optimize usage, recommended to re-read the README.
> ### 2024/1/27：Add jail break version, but image uploads are currently not supported, and python version need 3.10+.

![demo](https://i.imgur.com/mvg18xh.gif)

## Features

<details>
   <summary>
   
   ### Slash command

   </summary>
   
> ### will create a separate chat for each user.
   
* cookies setting (set for using personal Bing Cookies): `/cookies setting [cookies_file]`
  * Can upload own cookies (get from https://bing.com/). Supports simultaneous uploads.
  ![setting](https://i.imgur.com/ZTLKkAJ.png)

* Unofficial DALLE-3 api key setting (set for using personal unofficial DALLE-3 api key, can get from https://dalle.feiyuyu.net/dashboard): `/dalle3 setting`

  ![dalle3_setting](https://i.imgur.com/cSVBFov.png)
  
* copilot: `/copilot [version] [style] [type]`
  * A separate thread will be created, if use default version, can generate images while chatting.
    * [version]：`default` can chat with Copilot, `jailbreak` chat with Sydney, but `jailbreak` image uploads are not currently supported.
    * [style]：Have 3 conversation style can choose, `creative`、`balanced` and `precise`.
    * [type]：Options for thread type, `public` or `private`.
    * [plugin]：Currently only supports Suno.

  ![chat](https://i.imgur.com/3Fx0iQE.png)
  ![suno](https://i.imgur.com/G5FugDC.png)
  
* image creator: `/create image [service][prompt]`
  
  ![bingimage.png](https://i.imgur.com/pSCI1bg.png)
  ![dalle3image.png](https://i.imgur.com/o13jaln.png)

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
  ![mention1](https://i.imgur.com/BDy0See.png)
  ![mention2](https://i.imgur.com/iJg4pSg.png)

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
 
 * `!upload [.txt_file]`: Same as `/cookies setting`, but for default cookies.
 
   ![upload](https://i.imgur.com/Qqz07WA.png)
</details>

## Install
```
pip install -r requirements.txt
```

## Usage
1. Rename the file`.env.dev`to`.env`, then open it and edit it.
   ```env
    DISCORD_BOT_TOKEN=

    # (Optional) If you are run with Replit, it is recommended to configure cookies using this parameter instead of using cookies.json
    BING_COOKIES=

    # Timeout for BingImageCreator
    IMAGE_TIMEOUT=300
    IMAGE_MAX_CREATE_SEC=300

    # Set unofficial DALLE-3 api key, api key can get from https://dalle.feiyuyu.net/dashboard
    DALLE3_UNOFFICIAL_APIKEY=

    # (Optional) Allow mention bot only in specific channel.
    MENTION_CHANNEL_ID=1227670969702754857

    # (Optional) Allow each commands in some channels.
    # specific channel(s) for /cookies setting
    COOKIES_SETTING_CHANNEL_ID=1227670969702754857,1227327094070254857

    # specific channel(s) for /dalle3 setting
    DALLE3_SETTING_CHANNEL_ID=122767096970275483

    # specific channel(s) for /copilot
    CHAT_CHANNEL_ID=

    # specific channel(s) for /create image
    CREATE_IMAGE_CHANNEL_ID=

    # specific channel(s) for /reset conversation
    RESET_CHAT_CHANNEL_ID=

    # specific channel(s) for /help
    HELP_CMD_CHANNEL_ID=
   ```
   
2. Create the `cookies.json` file.
   * Install the cookie editor extension for Chrome or Firefox.
   * Go to [bing.com](https://www.bing.com/)
   * Click "Export" on the buttom right.
   * Paste your cookies into a file `cookies.json`

4. Start run your bot.
   ```python
   python bot.py

   ```

## Credits
* ReEdgeGPT - https://github.com/Integration-Automation/ReEdgeGPT

* Sydney  - https://github.com/juzeon/SydneyQt/tree/v1

* free-dall-e-proxy - https://github.com/Feiyuyu0503/free-dall-e-proxy

## Contributors

This project exists thanks to all the people who contribute.

[![](https://contrib.rocks/image?repo=FuseFairy/DiscordBot-EdgeGPT)](https://github.com/FuseFairy/DiscordBot-EdgeGPT/graphs/contributors)


## Star History
[![Star History Chart](https://api.star-history.com/svg?repos=FuseFairy/DiscordBot-EdgeGPT&type=Date)](https://star-history.com/#FuseFairy/DiscordBot-EdgeGPT&Date)
