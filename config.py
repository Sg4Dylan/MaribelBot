#MaribelBot CONFIG FILE

import plugins

# Bot ID
bot_id = "@MaribelBot"

# CALL GLOBALLY
global_trigger = [
    plugins.start,
    plugins.null
]
# CALL IN GROUP WITH SURFIX OR CALL IN PRIVATE
group_trigger = [
    plugins.help,
    plugins.five_in_one,
    plugins.tags_cloud,
    plugins.set_dl,
    plugins.safemodule,
    plugins.hdmode,
    plugins.null
]
# Callback
callback_trigger = [
    plugins.five_in_one,
    plugins.tags_cloud,
    plugins.null
]
