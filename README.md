# MaribelBot
另一个简单的 Telegram 图片 bot 
Yet another simple telegram bot which can return a random picture. 


演示
------------
* https://telegram.me/MaribelBot

依赖
------------
* Python 3.5.x
* [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
* Tornado
* nginx

部署
------------
1. 配置 nginx 反代 `http://127.0.0.1:8021/`； 
2. 在 `Maribel.py` 的 21 行处填上 bot 的 token； 
3. [设置你的 webhook](https://core.telegram.org/bots/api#setwebhook)； 
4. 运行 `python3 Maribel.py`； 
5. 和 bot 聊天使用指令，例如 `/konachan`