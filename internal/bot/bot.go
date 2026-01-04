package bot

import (
	"log"
	"time"

	"maribel-bot/config"
	"maribel-bot/internal/network"
	"maribel-bot/internal/plugins"

	tele "gopkg.in/telebot.v4"
)

var B *tele.Bot

func Start() {
	pref := tele.Settings{
		Token:  config.C.Bot.Token,
		Poller: &tele.LongPoller{Timeout: 10 * time.Second},
		Client: network.Client,
	}

	var err error
	B, err = tele.NewBot(pref)
	if err != nil {
		log.Fatal(err)
	}

	// 注册插件
	plugins.Register(B)

	log.Println("Maribel Lite Server started.")
	B.Start()
}