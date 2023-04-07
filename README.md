# DiscordBot-EdgeGPT
> ### Using Bing on discord bot, your Microsoft account needs to be able to access Bing first.
> 
## Update
> ### 2023/4/5 : Now can generate images by Bing Image Creator.
> ### 2023/3/20 : make buttons disable after a click.
> ### 2023/3/19 : make reply messages with suggestion reply buttons.

<details>
   <summary>
   
## Features (slash command)

   </summary>

* bing: `/bing [message]`

   | USE_SUGGEST_RESPONSES: True  (can change in file ```config.yml```) |
   |---|
  ![edgegpt](https://i.imgur.com/cLPL156.png)

   | USE_SUGGEST_RESPONSES: False (can change in file ```config.yml```) |
   |---|
  ![edgegpt](https://i.imgur.com/yK3P9Kt.png)
  
* bing image creator: `/create_image [prompt]`
  
  ![bingimage.png](https://i.ibb.co/0rxNbnk/2023-04-07-191036.png)
 
* conversation style (default balanced): `/switch_style [style]`
  
  ![style.png](https://i.ibb.co/54KMWKH/2023-04-07-200312.png)

* reset: `/reset`

  ![reset](https://i.imgur.com/AG5qQ1F.png)
</details>

## Install
```
git clone https://github.com/FuseFairy/DiscordBot-EdgeGPT.git
cd DiscordBot-EdgeGPT
pip install -r requirements.txt
```

## Usage
1. Rename the file`.env.dev`to`.env`, then open it and edit it.
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
* BingImageCreator - [https://github.com/acheong08/BingImageCreator](https://github.com/acheong08/BingImageCreator)
* other - [https://github.com/Zero6992/chatGPT-discord-bot](https://github.com/Zero6992/chatGPT-discord-bot)

## Contributors

This project exists thanks to all the people who contribute.

 <a href="https://github.com/FuseFairy/DiscordBot-EdgeGPT/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=FuseFairy/DiscordBot-EdgeGPT" />
 </a>
