package plugins

import (
	"fmt"
	tele "gopkg.in/telebot.v4"
)

func registerBasic(b *tele.Bot) {
	b.Handle("/start", func(c tele.Context) error {
		return c.Reply("Maribel Lite - A simple Telegram image bot.")
	})

	b.Handle("/help", func(c tele.Context) error {
		version := "20260103 - レゼ"
		msg := fmt.Sprintf(`<b>使用技巧：</b>
除 <i>TheAnimeGallery</i> 外，可在命令后追加合规的标签名限制结果范围
例如：<code>/konachan touhou</code>
除 <i>TheAnimeGallery</i> 外，可以在指令后追加 <code>#horizontal</code> 或 <code>#vertial</code> 来限制图片版式
例如：<code>/yandere#vertial touhou</code>

<b>特别服务：</b>
回复时间线上的任意 sticker <code>/PKSDL</code>，bot 可以帮您下载转换整组 sticker~

Current version：<code>%s</code>`, version)

		return c.Reply(msg, tele.ModeHTML)
	})
}