from tgfunc import *

help_msg = "<b>使用技巧：</b>" \
           "\n除 <i>TheAnimeGallery</i> 外，可在命令后追加合规的标签名限制结果范围" \
           "\n例如：<code>/konachan touhou</code>" \
           "\n除 <i>TheAnimeGallery</i> 外，可以在指令后追加 <code>#horizontal</code> 或 <code>#vertial</code> 来限制图片版式" \
           "\n例如：<code>/yandere#vertial touhou</code>" \
           "\n在群组中使用 Maribel 需额外 at Maribel 的 ID" \
           "\n例如：<code>/konachan@MaribelBot touhou</code> \n" \
           "\n当前版本：<code>20180818 - ユエ(Beta)</code>"

def help(update: dict) -> bool:
    try:
        if update['message'].get('text','').startswith("/help"):
            post_message(update, 2, help_msg)
            return True
        else:
            return False
    except:
        return False