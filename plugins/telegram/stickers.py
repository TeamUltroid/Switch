from . import command, Message, add_doc
from urllib.parse import urlparse

@command("tgsticker")
async def on_tgsticker(message: Message):
    try:
        sticker = message.message.split(" ", 1)[1]
    except IndexError:
        await message.edit_text("Invalid usage of command.")
        return
    parsed = urlparse(sticker)
    if "/addstickers" not in sticker:
        pass