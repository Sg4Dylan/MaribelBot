# MaribelBot
另一个简单的 Telegram 图片 bot 
Yet another simple telegram bot which can return a random picture. 

演示
------------
* https://telegram.me/MaribelBot

依赖
------------
* **Python 3.6+**
* Tornado
* requests
* BeautifulSoup4
* configparser
* coloredlogs
* Pillow
* nginx

部署
------------
1. 配置 nginx 反代 `http://127.0.0.1:8021/`； 
2. 在 `config.py` 填上 bot 自己的用户名； 
3. 在 `tgfunc/config.py` 里填上 Token 以及管理者的 ID； 
4. [设置你的 webhook](https://core.telegram.org/bots/api#setwebhook)； 
5. 运行 `python3 Maribel.py`； 
6. 和 bot 聊天使用指令，例如 `/konachan`