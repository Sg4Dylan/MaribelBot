package plugins

import tele "gopkg.in/telebot.v4"

func Register(b *tele.Bot) {
	registerBasic(b)
	registerAdmin(b)
	registerFiveInOne(b)
	registerSticker(b)
	registerTagCloud(b)
}