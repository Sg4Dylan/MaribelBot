package plugins

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"maribel-bot/config"
	"maribel-bot/internal/network"
	"math"
	"math/rand"
	"strings"

	tele "gopkg.in/telebot.v4"
)

var sites = map[string]struct{ url string; id int }{
	"/yandere":  {"https://yande.re/post.json?limit=100&", 0},
	"/konachan": {"https://konachan.com/post.json?limit=100&", 1},
	"/danbooru": {"https://danbooru.donmai.us/posts.json?limit=100&", 2},
}

func registerFiveInOne(b *tele.Bot) {
	// 1. 注册文本命令处理
	for cmd := range sites {
		b.Handle(cmd, func(c tele.Context) error {
			return executeFiveInOne(c, c.Text())
		})
	}

	// 2. 注册通用回调处理
	b.Handle(tele.OnCallback, func(c tele.Context) error {
		data := c.Callback().Data
		if data == "" {
			data = c.Callback().Unique
		} else if c.Callback().Unique != "" && !strings.Contains(data, c.Callback().Unique) {
			data = c.Callback().Unique + "|" + data
		}
		
		data = strings.TrimLeft(data, "\f")
		data = strings.TrimSpace(data)

		for cmd := range sites {
			if strings.HasPrefix(data, cmd) {
				c.Respond()
				return executeFiveInOne(c, data)
			}
		}
		return nil
	})
}

// 核心逻辑函数
func executeFiveInOne(c tele.Context, txt string) error {
	cmd := strings.Split(txt, " ")[0]
	if idx := strings.Index(cmd, "@"); idx != -1 {
		cmd = cmd[:idx]
	}

	siteInfo, ok := sites[cmd]
	if !ok {
		return nil
	}

	// 处理 #vertical / #horizontal
	screenType := 0 // 0: All, 1: Vertical, 2: Horizontal
	if strings.Contains(txt, "#vertical") {
		screenType = 1
	} else if strings.Contains(txt, "#horizontal") {
		screenType = 2
	}
	
	// 提取 Tag
	tags := ""
	parts := strings.SplitN(txt, " ", 2)
	if len(parts) > 1 {
		tags = parts[1]
		tags = strings.ReplaceAll(tags, "#vertical", "")
		tags = strings.ReplaceAll(tags, "#horizontal", "")
		tags = strings.TrimSpace(tags)
	}

	// 构造 URL
	page := rand.Intn(10) + 1
	reqURL := siteInfo.url + fmt.Sprintf("page=%d&tags=%s", page, tags)

	// 请求 API
	resp, err := network.Client.Get(reqURL)
	if err != nil {
		return c.Send("API Error")
	}
	defer resp.Body.Close()

	// 解析 JSON
	var posts []map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&posts)

	if len(posts) == 0 {
		return c.Send("No results found.")
	}

	// 过滤逻辑
	var filtered []map[string]interface{}
	safeMode := config.GetLegacyBool(config.C.Files.SafeModeIni, "SafeModule", c.Chat().ID, false)

	for _, post := range posts {
		w, _ := getInt(post, "width", "image_width", "sample_width")
		h, _ := getInt(post, "height", "image_height", "sample_height")
		
		if screenType == 1 && w >= h { continue }
		if screenType == 2 && w <= h { continue }

		if safeMode {
			rating, _ := getString(post, "rating")
			if rating != "s" && rating != "safe" {
				continue
			}
		}
		
		fileUrl, _ := getString(post, "file_url", "large_file_url")
		if fileUrl == "" { continue }

		filtered = append(filtered, post)
	}

	if len(filtered) == 0 {
		return c.Send("No results after filtering.")
	}

	// 随机选择
	target := filtered[rand.Intn(len(filtered))]

	// 准备数据
	postID, _ := getInt(target, "id")
	fileURL, _ := getString(target, "file_url", "large_file_url")
	sampleURL, _ := getString(target, "sample_url")
	
	if strings.HasPrefix(fileURL, "//") { fileURL = "https:" + fileURL }
	if strings.HasPrefix(sampleURL, "//") { sampleURL = "https:" + sampleURL }
	if !strings.HasPrefix(fileURL, "http") { fileURL = "https://" + fileURL }
	
	if sampleURL == "" || sampleURL == "https:" { sampleURL = fileURL }

	// HD Mode 逻辑
	hdMode := config.GetLegacyBool(config.C.Files.HdModeIni, "HD-Mode", c.Chat().ID, false)
	dlURL := sampleURL
	if hdMode {
		dlURL = fileURL
	}

	c.Notify(tele.UploadingPhoto)

	// 内存下载
	imgResp, err := network.Client.Get(dlURL)
	if err != nil || imgResp.StatusCode != 200 {
		dlURL = sampleURL
		imgResp, err = network.Client.Get(dlURL)
		if err != nil {
			return c.Send("Download Failed")
		}
	}
	defer imgResp.Body.Close()

	var buf bytes.Buffer
	io.Copy(&buf, imgResp.Body)

	// --- 构造 UI ---

	originPage := getOriginPage(siteInfo.id, postID)
	siteName := strings.ReplaceAll(cmd, "/", "")
	siteName = strings.ToUpper(siteName[:1]) + siteName[1:]
	
	fileSizeStr := convertSize(int64(buf.Len()))
	
	caption := fmt.Sprintf("%s ID: <a href=\"%s\">%d</a> File size: %s", 
		siteName, originPage, postID, fileSizeStr)
	
	if c.Callback() != nil {
		userLink := fmt.Sprintf("tg://user?id=%d", c.Sender().ID)
		caption += fmt.Sprintf(" - by <a href=\"%s\">user</a>", userLink)
	}

	menu := &tele.ReplyMarkup{}
	btnSource := menu.URL("查看原图 View source", fileURL)
	btnAgain := menu.Data("再来一张 Once again", txt) 

	menu.Inline(
		menu.Row(btnSource, btnAgain),
	)

	return c.Reply(&tele.Photo{
		File:    tele.FromReader(&buf),
		Caption: caption,
	}, tele.ModeHTML, menu)
}

// --- Helper Functions ---

func convertSize(sizeBytes int64) string {
	if sizeBytes == 0 {
		return "0B"
	}
	sizeName := []string{"B", "KiB", "MiB", "GiB", "TiB"}
	i := int(math.Floor(math.Log(float64(sizeBytes)) / math.Log(1024)))
	p := math.Pow(1024, float64(i))
	s := math.Round((float64(sizeBytes)/p)*100) / 100
	return fmt.Sprintf("%.2f %s", s, sizeName[i])
}

func getOriginPage(siteID, postID int) string {
	switch siteID {
	case 0: return fmt.Sprintf("https://yande.re/post/show/%d", postID)
	case 1: return fmt.Sprintf("https://konachan.com/post/show/%d", postID)
	case 2: return fmt.Sprintf("https://danbooru.donmai.us/posts/%d", postID)
	default: return ""
	}
}

func getInt(m map[string]interface{}, keys ...string) (int, bool) {
	for _, k := range keys {
		if v, ok := m[k]; ok {
			switch val := v.(type) {
			case float64: return int(val), true
			case int: return val, true
			}
		}
	}
	return 0, false
}

func getString(m map[string]interface{}, keys ...string) (string, bool) {
	for _, k := range keys {
		if v, ok := m[k]; ok {
			if s, ok := v.(string); ok {
				return s, true
			}
		}
	}
	return "", false
}