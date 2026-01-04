# MaribelBot
另一个简单的 Telegram 图片 bot  
Yet another simple telegram bot which can return a random picture. 

演示
------------
* https://telegram.me/MaribelBot

依赖
------------
* **Go 1.25+** 
* *zig* (可选，用于 CGO 编译)

部署
------------
1. 在 BotFather 创建一个 bot 并取得 Token；
2. 在 `config.yaml` 里填上 Token 以及管理者的 ID； 
3. 运行 `./Maribel`； 
4. 和 bot 聊天使用指令，例如 `/konachan`