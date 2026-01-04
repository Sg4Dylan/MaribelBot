package network

import (
	"maribel-bot/config"
	"net/http"
	"net/url"
	"time"
)

var Client *http.Client

func Init() {
	transport := &http.Transport{}
	if config.C.Bot.Proxy != "" {
		proxyURL, err := url.Parse(config.C.Bot.Proxy)
		if err == nil {
			transport.Proxy = http.ProxyURL(proxyURL)
		}
	}
	Client = &http.Client{
		Transport: transport,
		Timeout:   60 * time.Second,
	}
}