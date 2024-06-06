from re import compile
from . import command, Message, add_doc
from config import Config

@command("set")
async def on_set(message: Message):
    try:
        split = message.message.split()
        variable = split[1]
    except IndexError:
        await message.reply_text("Invalid usage of command.")
        return

    if variable == "ALIVE_MEDIA":
        replied = await message.get_replied_message()
        if not (replied and replied.media_info):
            await message.edit_text("Reply to a media message.")
            return
        value = replied.media_info.id
    else:
        await message.reply_text("Invalid variable.")
        return
    Config.set(f"VAR_{variable}", value)
    await message.edit_text("Variable set successfully!")

 
@command("del")
async def on_delete(message: Message):
    try:
        split = message.message.split()
        variable = split[1]
    except IndexError:
        await message.reply_text("Invalid usage of command.")
        return
    Config.delete(f"VAR_{variable}")
    await message.edit_text("Variable deleted successfully!")

@command("getkeys")
async def get_keys(m: Message):
    keys = Config.keys()
    response = "Here are the available variables:\n\n"
    for key in keys:
        response += f"- `{key}`\n"
    await m.edit_text(response.strip())

add_doc(
    "Variables" , ["set", "del", "getkeys"]
)