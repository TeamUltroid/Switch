from . import command, Message, LOGS
from functions.messages import getAllMessages


@command("copychat")
async def copyChatMessage(m: Message):
    """Copy messages from a chat to the current chat."""
    try:
        chatId = m.message.split(maxsplit=1)[1]
    except IndexError:
        return await m.edit_text("Invalid usage of command.")
    app = m.app
    channel, group = None, None
    try:
        channel = await app.get_channel(chatId)
    except Exception as er:
        LOGS.exception(er)
        try:
            group = await app.get_group(chatId)
        except Exception as er:
            LOGS.exception(er)
            return await m.edit_text("Invalid chat ID.")
    chat = channel or group
    await m.edit_text(f"Copying messages from {chat.icon} {chat.name}...\nIt may take some time, depending on number of messages!")
    messageBox = await getAllMessages(
        chat_id=chat.id, community_id=chat.community_id, group=bool(group)
    )
    messageBox.reverse()
    await app.forward_message(
        [mId.id for mId in messageBox], m.group_id or m.channel_id, m.receiver_id
    )
    await m.reply_text(f"✅ Messages copied from {chat.icon} {chat.name}!")
    await m.delete()