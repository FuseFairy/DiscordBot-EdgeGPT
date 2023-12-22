# DiscordBot-EdgeGPT
> ## Using Microsoft's Bing Chat AI and Bing Image Creator on discord bot.
![demo](https://i.imgur.com/Kc1aP9M.gif)

## Update
> ### 2023/12/22：Support uploading image while chatting.
> ### 2023/11/13：Use another bing api instead.
> ### 2023/6/21：fix Redirect failed when using Creative style to create images.
> ### 2023/6/1：Users not need to set cookies also can use slash command.
> ### 2023/5/21：Anyone who wants to use slash command should set their cookies first.
   
## Features

<details>
   <summary>
   
   ### Slash command

   </summary>
   
> ### will create a separate chat for each user.
   
* cookies setting(can use personal Bing Cookies): `/bing setting [choice]`
  ![setting](https://i.imgur.com/GMLQpCF.png)
  
   
* bing: `/bing [message] [image]`

  ![edgegpt](https://i.imgur.com/cLPL156.png)
  
* bing image creator: `/create image [prompt]`
  
  ![bingimage.png](https://i.imgur.com/xxIAR09.png)
 
* conversation style (default balanced): `/switch style [style]`
  
  ![style.png](https://i.imgur.com/bs4tmZr.png)

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
 
 * `!upload [.txt_file]`: Because Bing Cookies will expire, so this command can set new Cookies directly. You just need to copy bing cookies and past,                           the Cookies will auto convert to .txt file.
 
   ![upload](https://i.imgur.com/UN1Ac7N.png)
</details>

## Install
```
pip install -r requirements.txt
```

## Usage
1. Rename the file`.env.dev`to`.env`, then open it and edit it. If you don't want a limit channel to mention a bot, you don't need to set up a   MENTION_CHANNEL_ID, just leave it blank.
   ```
   DISCORD_BOT_TOKEN=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   MENTION_CHANNEL_ID=123456789
   ```
   
2. Create `cookies.json` file, and get Bing authentication.
   * Install the cookie editor extension for Chrome or Firefox.
   * Go to [bing.com](http://bing.com/chat)
   * Click "Export" on the bottom right.
   * Paste your cookies into a file `cookies.json`

4. Start run your bot, hosted locally or on a server.

   -> Recommended Free Servers: [fly.io](https://fly.io/)

## Credits
* ReEdgeGPT - [https://github.com/Integration-Automation/ReEdgeGPT](https://github.com/Integration-Automation/ReEdgeGPT)

## Contributors

This project exists thanks to all the people who contribute.

[![](https://contrib.rocks/image?repo=FuseFairy/DiscordBot-EdgeGPT)](https://github.com/FuseFairy/DiscordBot-EdgeGPT/graphs/contributors)
