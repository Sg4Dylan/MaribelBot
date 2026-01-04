package plugins

import (
	"fmt"
	"maribel-bot/config"
	"strings"

	tele "gopkg.in/telebot.v4"
)

func registerAdmin(b *tele.Bot) {
	b.Handle("/hdmode", func(c tele.Context) error { return handleModeSwitch(c, "hd") })
	b.Handle("/safemode", func(c tele.Context) error { return handleModeSwitch(c, "safe") })
}

func handleModeSwitch(c tele.Context, modeType string) error {
	iniPath := config.C.Files.SafeModeIni
	section := "SafeModule"
	if modeType == "hd" {
		iniPath = config.C.Files.HdModeIni
		section = "HD-Mode"
	}

	args := c.Args()
	if len(args) == 0 {
		status := config.GetLegacyBool(iniPath, section, c.Chat().ID, false)
		statusText := "OFF"
		if status { statusText = "ON" }
		return c.Reply(fmt.Sprintf("%s Mode: %s", strings.ToUpper(modeType), statusText))
	}

	if !checkGroupAdmin(c) {
		return c.Reply("Admin required.")
	}

	switch strings.ToUpper(args[0]) {
	case "ON":
		config.SetLegacyBool(iniPath, section, c.Chat().ID, true)
		c.Reply(fmt.Sprintf("%s Mode ON", strings.ToUpper(modeType)))
	case "OFF":
		config.SetLegacyBool(iniPath, section, c.Chat().ID, false)
		c.Reply(fmt.Sprintf("%s Mode OFF", strings.ToUpper(modeType)))
	}
	return nil
}

func checkGroupAdmin(c tele.Context) bool {
	if c.Chat().Type == tele.ChatPrivate { return true }
	// 检查单管理员 ID
	if c.Sender().ID == config.C.Bot.AdminID { return true }

	member, err := c.Bot().ChatMemberOf(c.Chat(), c.Sender())
	if err != nil { return false }
	return member.Role == tele.Administrator || member.Role == tele.Creator
}