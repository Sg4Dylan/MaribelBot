package plugins

import (
	"encoding/json"
	"maribel-bot/internal/network"
	"math/rand"

	tele "gopkg.in/telebot.v4"
)

func registerTagCloud(b *tele.Bot) {
	// Level 1 Menu
	menu := &tele.ReplyMarkup{}
	btnYandere := menu.Data("Yandere", "type_yandere")
	btnKonachan := menu.Data("Konachan", "type_konachan")
	btnDanbooru := menu.Data("Danbooru", "type_danbooru")

	menu.Inline(
		menu.Row(btnYandere, btnKonachan),
		menu.Row(btnDanbooru),
	)

	b.Handle("/tagcloud", func(c tele.Context) error {
		return c.Reply("请选择Tag来源 Please choose tag source:", menu)
	})

	// Level 2 Handler
	handleTagSource := func(c tele.Context, apiUrl, cmdPrefix string) error {
		resp, err := network.Client.Get(apiUrl)
		if err != nil { return c.Respond() }
		defer resp.Body.Close()

		var tags []map[string]interface{}
		json.NewDecoder(resp.Body).Decode(&tags)

		if len(tags) == 0 { return c.Respond() }

		// Build Grid
		tagMenu := &tele.ReplyMarkup{}
		var rows []tele.Row

		rand.Shuffle(len(tags), func(i, j int) { tags[i], tags[j] = tags[j], tags[i] })
		limit := 15
		if len(tags) < 15 { limit = len(tags) }
		
		currentTags := tags[:limit]
		var currentRow []tele.Btn

		for _, t := range currentTags {
			name := t["name"].(string)
			currentRow = append(currentRow, tagMenu.Data(name, cmdPrefix + name))
			
			if len(currentRow) == 4 {
				rows = append(rows, tagMenu.Row(currentRow...))
				currentRow = []tele.Btn{}
			}
		}

		// Reroll & Back
		currentType := c.Callback().Unique
		if currentType == "" {
			currentType = c.Callback().Data
		}
		
		btnReroll := tagMenu.Data("Reroll 💦", currentType) 
		btnBack := tagMenu.Data("🔙 Back", "retake_menu")
		
		currentRow = append(currentRow, btnBack, btnReroll)
		rows = append(rows, tagMenu.Row(currentRow...))
		tagMenu.Inline(rows...)

		return c.Edit("请点击你需要获取的标签 Click the label you need:", tagMenu)
	}

	b.Handle(&btnYandere, func(c tele.Context) error {
		return handleTagSource(c, "https://yande.re/tag.json?order=count&limit=200", "/yandere ")
	})
	b.Handle(&btnKonachan, func(c tele.Context) error {
		return handleTagSource(c, "https://konachan.com/tag.json?order=count&limit=200", "/konachan ")
	})
	b.Handle(&btnDanbooru, func(c tele.Context) error {
		return handleTagSource(c, "https://danbooru.donmai.us/tags.json?order=count&limit=200", "/danbooru ")
	})

	b.Handle(&tele.Btn{Unique: "retake_menu"}, func(c tele.Context) error {
		return c.Edit("请选择Tag来源 Please choose tag source:", menu)
	})
}