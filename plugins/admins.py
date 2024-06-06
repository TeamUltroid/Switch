import asyncio
from . import command, Message, add_doc
from functions.messages import sendDelete


@command("delete", community_only=True)
async def on_cleanchat(message: Message):
    """
    Command to delete all messages in a chat.
    """
    mSplit = message.message.split()
    try:
        param = mSplit[1]
    except IndexError:
        param = None
    replied = await message.get_replied_message()
    if replied and "all" not in mSplit:
        await replied.delete()
        return await message.edit_text("🗑️ Message deleted.")
    message = await message.reply_text("__Cleaning chat...__")
    user_id = (replied or message).user_id
    delete_count = 0
    offset = 0
    while True:
        if message.group_id:
            messages = await message.app.get_group_chat_history(
                message.group_id,
                message.community_id,
                page_offset=offset,
            )
        else:
            messages = await message.app.get_channel_chat_history(
                message.chat_id, message.community_id, page_offset=offset
            )
        if not messages.messages:
            break
        mBox = []
        for msg in messages.messages:
            if param == "all" or msg.user_id == user_id:

                if ("text" in mSplit and msg.media_info) or (
                    "media" in mSplit and not msg.media_info
                ):
                    continue
                mBox.append(msg.id)
        await message.app.delete_messages(mBox)
        delete_count += len(mBox)
        offset += 1
    await sendDelete(message, f"__Deleted {delete_count} messages.__")


@command("info")
async def info_command(message: Message):
    """Fetches information about a user or community."""
    response = ""
    if message.personal_chat:
        user = message.user
        response += "👤 *User Info*\n"
        response += f"  *Name:* <copy>{user.first_name} {user.last_name}</copy>\n"
        response += f"  *Username:* @{user.username}\n"
        response += f"  *User ID:* `{user.id}`\n"
        if user.is_bot:
            response += f"  User is a bot: {user.is_bot}\n"
        if user.bio:
            response += f"  Bio: {user.bio}"
    elif message.community_id:
        community = await message.app.get_community(message.community_id)
        response += "👥 *Community Info*\n\n"
        response += f"  *Name:* {community.name}\n"
        response += f"  *Community ID:* `{community.id}`\n"
        if community.username:
            response += f"  *Username:* @{community.username}\n"
        response += f"  *Type:* {community.type}\n"
        response += f"  *Description:* {community.description}\n"
        response += f"  *Link:* {community.link}\n"
        response += f"  *Channels:* {community.channels_count} | *Groups:* {community.groups_count}\n"
        response += f"  *Members:* {community.members_count}\n"
    else:
        return
    await message.edit_text(response.strip())


add_doc("Admins", ["delete", "info"])
