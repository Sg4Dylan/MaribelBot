package plugins

import (
	"archive/zip"
	"bytes"
	"fmt"
	"io"
	"sync"

	tele "gopkg.in/telebot.v4"
)

func registerSticker(b *tele.Bot) {
	// 显式注册命令 /PKSDL (Telebot 命令不区分大小写)
	b.Handle("/pksdl", func(c tele.Context) error {
		// 检查是否回复了贴纸
		if c.Message().ReplyTo == nil || c.Message().ReplyTo.Sticker == nil {
			return nil
		}

		setName := c.Message().ReplyTo.Sticker.SetName
		if setName == "" {
			return nil
		}

		statusMsg, _ := c.Bot().Send(c.Chat(), "正在解析 Sticker Set...\n`Resolving Sticker Set...`", tele.ModeMarkdown)

		set, err := c.Bot().StickerSet(setName)
		if err != nil {
			c.Bot().Edit(statusMsg, "解析失败 (Failed)")
			return nil
		}

		buf := new(bytes.Buffer)
		zw := zip.NewWriter(buf)

		var wg sync.WaitGroup
		var zipLock sync.Mutex
		sem := make(chan struct{}, 5)

		c.Bot().Edit(statusMsg, fmt.Sprintf("正在下载 %d 张贴纸...", len(set.Stickers)))

		for _, s := range set.Stickers {
			wg.Add(1)
			go func(sticker tele.Sticker) {
				defer wg.Done()
				sem <- struct{}{}
				defer func() { <-sem }()

				rc, err := c.Bot().File(&sticker.File)
				if err != nil {
					return
				}
				defer rc.Close()

				data, err := io.ReadAll(rc)
				if err != nil {
					return
				}

				ext := ".png"
				if sticker.Animated { ext = ".tgs" }
				if sticker.Video { ext = ".mp4" }

				zipLock.Lock()
				w, _ := zw.Create(sticker.FileID + ext)
				w.Write(data)
				zipLock.Unlock()
			}(s)
		}

		wg.Wait()
		zw.Close()

		c.Bot().Delete(statusMsg)
		c.Notify(tele.UploadingDocument)

		return c.Reply(&tele.Document{
			File:     tele.FromReader(buf),
			Caption:  fmt.Sprintf("Sticker Set: %s", set.Title),
			FileName: setName + ".zip",
			MIME:     "application/zip",
		})
	})
}