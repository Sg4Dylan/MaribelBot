from tgfunc import *

def help(update: dict) -> bool:
    try:
        if u'/help' in update['message']['text']:
            help_msg = "关于标签搜索：" \
                       "\n除 `TheAnimeGallery` 外，其他来源可以在命令后加入 `tag` 获取该 `tag` 下的图片" \
                       "\n例如：`/konachan touhou`" \
                       "\n另外，在群组使用 Maribel 要记得 at Maribel 的 ID" \
                       "\n例如：`/konachan@MaribelBot touhou` \n" \
                       "\n当前版本：`20170824 - Cavendish(Stable)`"
            send_message(update, True, help_msg)
            return True
        else:
            return False
    except:
        return False