package config

import (
	"strconv"
	"sync"
	"gopkg.in/ini.v1"
)

var iniMutex sync.RWMutex

func GetLegacyBool(path string, section string, chatID int64, fallback bool) bool {
	iniMutex.RLock()
	defer iniMutex.RUnlock()

	f, err := ini.Load(path)
	if err != nil {
		return fallback
	}
	return f.Section(section).Key(strconv.FormatInt(chatID, 10)).MustBool(fallback)
}

func SetLegacyBool(path string, section string, chatID int64, value bool) {
	iniMutex.Lock()
	defer iniMutex.Unlock()

	f, err := ini.Load(path)
	if err != nil {
		f = ini.Empty()
	}
	sec := f.Section(section)
	sec.Key(strconv.FormatInt(chatID, 10)).SetValue(strconv.FormatBool(value))
	sec.Key("using").SetValue("True")
	f.SaveTo(path)
}