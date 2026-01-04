package main

import (
	"maribel-bot/config"
	"maribel-bot/internal/bot"
	"maribel-bot/internal/network"
)

func main() {
	// 1. 加载配置
	config.Load("config.yaml")

	// 2. 初始化网络
	network.Init()

	// 3. 启动 Bot
	bot.Start()
}