#MaribelBot CONFIG FILE

import plugins

# Bot Name
bot_id = "@MaribelBot"

# CALL GLOBALLY
global_trigger = [
    plugins.safemodule,
    plugins.hdmode,
    plugins.start,
    plugins.callback_process,
    plugins.null
]
# CALL IN GROUP WITH SURFIX OR CALL IN PRIVATE
group_trigger = [
    plugins.help,
    plugins.five_in_one,
    plugins.theanimegallery,
    plugins.tags_cloud,
    plugins.null
]
