from . import command, Message, tg_bot, user
from urllib.parse import urlparse
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.types import InputStickerSetShortName
from telethon.tl.types.messages import StickerSet
import os


async def get_telegram_stickers(short_name: str) -> tuple:
    stickers: StickerSet = await tg_bot(
        GetStickerSetRequest(
            stickerset=InputStickerSetShortName(short_name=short_name), hash=0
        )
    )
    sticker_set_type, _stickers = None, {}
    for sticker in stickers.documents:
        set_type = {
            "image/webp": ("STATIC", "webp"),
            "application/x-tgsticker": ("ANIMATED", "tgs"),
            "video/webm": ("VIDEO", "webm"),
        }
        if not sticker_set_type:
            sticker_set_type = set_type[sticker.mime_type]
        _stickers[
            await tg_bot.download_media(sticker, f"{sticker.id}.{sticker_set_type[1]}")
        ] = sticker.attributes[1].alt
    return (sticker_set_type[0], _stickers)


@command("tgsticker")
async def on_tgsticker(message: Message):
    try:
        sticker = message.message.split(" ", 1)[1]
    except IndexError:
        await message.edit_text("Invalid usage of command.")
        return
    parsed = urlparse(sticker)
    if "/addstickers" not in sticker:
        return await message.edit_text("Give sticker set link.")
    sticker_short_name = parsed.path.split("/")[-1]
    await message.edit_text("Processing...")
    sticker_pack_type, stickers = await get_telegram_stickers(
        short_name=sticker_short_name
    )
    if not sticker_pack_type == "STATIC":
        return await message.edit_text("Not implemented.")
    stickerpack = await user.create_sticker_pack(
        name=sticker_short_name,
        pack_type=sticker_pack_type,
        thumb=list(stickers.keys())[0],
    )
    for sticker in stickers.keys():
        await user.create_sticker(
            sticker=sticker,
            name=sticker,
            description="",
            emoji=stickers[sticker],
            pack_id=stickerpack.id,
        )
        os.remove(sticker)
    await message.edit_text(
        f"Go away. {sticker_short_name} created with id {stickerpack.id}!"
    )
