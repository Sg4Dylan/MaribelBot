package config

import (
	"fmt"
	"github.com/spf13/viper"
)

var C Config

type Config struct {
	Bot   BotConfig   `mapstructure:"bot"`
	Files FilesConfig `mapstructure:"files"`
}

type BotConfig struct {
	Token   string `mapstructure:"token"`
	Proxy   string `mapstructure:"proxy"`
	AdminID int64  `mapstructure:"admin_id"`
}

type FilesConfig struct {
	HdModeIni   string `mapstructure:"hd_mode_ini"`
	SafeModeIni string `mapstructure:"safe_mode_ini"`
}

func Load(path string) {
	viper.SetConfigFile(path)
	if err := viper.ReadInConfig(); err != nil {
		panic(fmt.Errorf("fatal error config file: %w", err))
	}
	if err := viper.Unmarshal(&C); err != nil {
		panic(err)
	}
}