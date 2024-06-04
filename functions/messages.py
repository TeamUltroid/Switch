import asyncio
from swibots import Message
from client import user
from typing import List

async def sendDelete(message: Message, text: str, delay: int = 5):
    s = await message.reply_text(text)
    await asyncio.sleep(delay)
    await s.delete()


async def getAllMessages(chat_id: str, community_id: str, group=False) -> List[Message]:
    messages = []
    offset = 0
    while True:
        if group:
            resp = await user.get_group_chat_history(
                chat_id, community_id, page_offset=offset
            )
        else:
            resp = await user.get_channel_chat_history(
                chat_id, community_id, page_offset=offset
            )
        if not resp.messages:
            break
        messages.extend(resp.messages)
        offset += 1
    return messages
