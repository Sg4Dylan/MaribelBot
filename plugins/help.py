from tgfunc import *

help_msg = "<b>使用技巧：</b>" \
           "\n除 <i>TheAnimeGallery</i> 外，可在命令后追加合规的标签名限制结果范围" \
           "\n例如：<code>/konachan touhou</code>" \
           "\n除 <i>TheAnimeGallery</i> 外，可以在指令后追加 <code>#horizontal</code> 或 <code>#vertial</code> 来限制图片版式" \
           "\n例如：<code>/yandere#vertial touhou</code>" \
           "\n<b>特别服务：</b>" \
           "\n回复时间线上的任意 sticker <code>/PKSDL</code>，bot 可以帮您下载转换整组 sticker~\n" \
           "\n<b>Tips:</b>" \
           "\nBesides <i>TheAnimeGallery</i>, you can add a tag name after the command to limit the result range." \
           "\nExample：<code>/konachan touhou</code>" \
           "\nBesides <i>TheAnimeGallery</i> , you can add <code>#horizontal</code> or <code>#vertial</code> after the command to limit the picture direction." \
           "\nExample：<code>/yandere#vertial touhou</code>" \
           "\n<b>Special service: </b>" \
           "\nReply to any sticker <code>/PKSDL</code>, bot can give you entire set of stickers~\n" \
           "\nCurrent version：<code>20210107 - カゼ(Beta)</code>"

def help(update: dict) -> bool:
    try:
        if update['message'].get('text','').startswith("/help"):
            post_message(update, 2, help_msg)
            return True
        else:
            return False
    except:
        return False