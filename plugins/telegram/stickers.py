import os, shutil, asyncio

from . import command, Message, tg_bot, user, add_doc, LOGS
from urllib.parse import urlparse
from functions.progress import get_progress_bar
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.types import InputStickerSetShortName
from telethon.tl.types.messages import StickerSet


async def get_telegram_stickers(
    short_name: str, folder: str, m: Message, limit: int = 50
) -> tuple:
    stickers: StickerSet = await tg_bot(
        GetStickerSetRequest(
            stickerset=InputStickerSetShortName(short_name=short_name), hash=0
        )
    )
    sticker_set_type, _stickers = None, {}
    count = len(stickers.documents[:limit])
    for index, sticker in enumerate(stickers.documents[:limit], start=1):
        set_type = {
            "image/webp": ("STATIC", "webp"),
            "application/x-tgsticker": ("ANIMATED", "tgs"),
            "video/webm": ("VIDEO", "webm"),
        }
        if not sticker_set_type:
            sticker_set_type = set_type[sticker.mime_type]
        _stickers[
            await tg_bot.download_media(
                sticker, f"{folder}/{sticker.id}.{sticker_set_type[1]}"
            )
        ] = sticker.attributes[1].alt
        if (index % 5) == 0:
            proc = get_progress_bar((index / count) * 100)
            await m.edit_text(f"Downloading {index}/{count} Stickers\n{proc}")
    await m.edit_text(f"*Downloaded {count} Stickers*!")
    return (sticker_set_type[0], _stickers, stickers.set.title or short_name)


@command("tgsticker")
async def on_tgsticker(message: Message):
    """Import telegram sticker packs to switch"""
    try:
        cmdSplit = message.message.split()
        sticker = cmdSplit[1]
    except IndexError:
        await message.edit_text("Invalid usage of command.")
        return
    try:
        stickersLimit = int(cmdSplit[2])
    except (TypeError, IndexError):
        stickersLimit = 50

    parsed = urlparse(sticker)
    folder_path = f"stickers_{message.id}"
    os.mkdir(folder_path)

    if "/addstickers" not in sticker:
        return await message.edit_text("Give sticker set link.")
    sticker_short_name = parsed.path.split("/")[-1]
    await message.edit_text("Processing...")
    sticker_pack_type, stickers, stitle = await get_telegram_stickers(
        short_name=sticker_short_name,
        folder=folder_path,
        m=message,
        limit=stickersLimit,
    )
    if not sticker_pack_type == "STATIC":
        return await message.edit_text("Not implemented.")

    stickerpack = await user.create_sticker_pack(
        name=stitle,
        pack_type=sticker_pack_type,
        thumb=list(stickers.keys())[0],
    )
    count = len(stickers)
    stickerZero = None
    for index, sticker in enumerate(stickers.keys(), start=1):
        s_response = await user.create_sticker(
            sticker=sticker,
            name=sticker,
            description="",
            emoji=stickers[sticker],
            pack_id=stickerpack.id,
        )
        if index == 1:
            stickerZero = s_response
        elif (index % 5) == 0:
            proc = get_progress_bar((index / count) * 100)
            await message.edit_text(f"*Uploading {index}/{count} Stickers*\n\n{proc}")
    await user.install_sticker_set(pack_id=stickerpack.id)
    # remove stickers folder
    try:
        shutil.rmtree(folder_path)
    except Exception as er:
        LOGS.exception(er)
    await message.edit_text(
        f"🏷️ *{stitle} created (`{stickerpack.id}`)!*\nAdded to your account!"
    )
    if stickerZero:
        # send first sticker after adding sticker pack
        m = await user.get_media(stickerZero.media_id)
        m.id = 0
        s = await message.send("", media_info=m)


add_doc("Stickers", ["tgsticker"])
