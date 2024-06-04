import os
import asyncio
from . import command, Message, add_doc, LOGS
from functions.parsers import parse_ms, format_file_size
from functions.progress import get_progress_bar, Timer, upload_progress
from telethon import TelegramClient
from urllib.parse import urlparse
from .fastTelethon import download_file


async def tg_download_progress(d, t, m: Message, text, can_send):
    if not can_send():
        return
    perc = (d / t) * 100
    message = f"""🔽 {text}\n [{format_file_size(d)} of {format_file_size(t)}]

{get_progress_bar(perc)} {perc:.2f}%"""
    await m.edit_text(message)


@command("tgimport")
async def downloadFromTg(m: Message):
    from plugins.telegram import tg_bot

    if not tg_bot:
        return await m.edit_text("Telegram bot not set up.")
    try:
        url = m.message.split(maxsplit=1)[1]
    except Exception as er:
        return await m.edit_text("Invalid usage of command.")
    splitted = urlparse(url).path.split("/")[1:]
    if len(splitted) != 2 or "t.me" not in url:
        return await m.edit_text("Invalid URL.")
    if splitted[0].isdigit():
        return await m.edit_text("Private groups or channels are not supported.")

    m = await m.edit_text("Downloading from Telegram...")
    tg_msg = await tg_bot.get_messages(splitted[0], ids=int(splitted[1]))
    await messageImport(tg_msg, m)
    await m.edit_text("✅ *Uploaded!*")


@command("tgchatimport")
async def downloadMessagesFromTg(m: Message):
    from plugins.telegram import tg_bot

    if not tg_bot:
        return await m.edit_text("Telegram bot not set up.")
    s_bot = await m.edit_text("Cool! Now send the link of start message.")
    startMessage = await m.listen()
    await startMessage.delete()
    if startMessage.message == "/cancel":
        await s_bot.edit_text("Task Cancelled!")
        return
    await s_bot.edit_text("Now send the link of end message.")
    endMessage = await m.listen()
    await endMessage.delete()
    if endMessage.message == "/cancel":
        await m.delete()
        await startMessage.delete()
        await s_bot.edit_text("Task Cancelled!")
        return
    try:
        chatId = startMessage.message.split("/")[-2]
        startId = int(startMessage.message.split("/")[-1])
        endId = int(endMessage.message.split("/")[-1]) + 1
    except Exception as er:
        await m.edit_text(f"ERROR Occured: {er}")
        return
    async for message in tg_bot.iter_messages(chatId, ids=list(range(startId, endId))):
        if message:
            try:
                await messageImport(message, m, inBulk=True)
            except Exception as er:
                LOGS.exception(er)
                await m.edit_text(f"ERROR Occured: {er}")
    await m.delete()
    await m.reply_text("✅ *Messages Imported!*")


async def messageImport(tg_msg, m: Message, inBulk: bool = False):
    from client import tg_bot

    name = None
    if tg_msg.media:

        name = tg_msg.file.name if tg_msg.file else None
        if not name:
            name = f"{tg_msg.id}.jpg"

        timer = Timer()
        with open(name, "wb") as f:
            await download_file(
                tg_bot,
                location=tg_msg.document,
                progress_callback=lambda d, t: asyncio.create_task(
                    tg_download_progress(
                        d,
                        t,
                        m,
                        f"*Downloading* <copy>{name}</copy>",
                        can_send=timer.can_send,
                    )
                ),
                out=f,
            )
        await m.edit_text(
            f"💖 *Download complete.*\n\n *Uploading* {name} [{format_file_size(tg_msg.file.size)}]..."
        )
        await m.reply_media(
            document=name,
            progress=upload_progress,
            progress_args=(m, timer.can_send),
            message=tg_msg.text
            or (
                None
                if inBulk
                else f"⚡ *Downloaded from Telegram.*\n\n📦 *File:* {name}\n📏 *Size:* {format_file_size(tg_msg.file.size)}"
            ),
        )
        if name:
            os.remove(name)
    elif tg_msg.text:
        await m.reply_text(tg_msg.text)
