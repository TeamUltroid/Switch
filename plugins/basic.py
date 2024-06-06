import sys, os
import time, json
from . import command, Message, add_doc, LOGS
from functions.parsers import parse_ms
from config import VERSION, START_TIME, Config
from core.constants import PLUGINS_MENU, HELP_MENU
from sys import version_info, platform
from swibots import InlineKeyboardButton
from client import LOG_PATH


@command("ping")
async def on_ping(message: Message):
    """Check the bot's response time."""
    start_time = time.time()
    replied = await message.edit_text("Pong!")
    diff = (time.time() - start_time) * 100
    await replied.edit_text("❣️ *Pong!*\n" + f"⚡ Response: {diff:.2f}ms")


@command("alive")
async def on_alive(message: Message):
    """Check if the bot is alive."""
    try:
        await message.delete()
    except:
        pass
    media = Config.get("VAR_ALIVE_MEDIA")
    if media:
        try:
            media = await message.app.get_media(int(media))
            media.id = 0
        except Exception as e:
            media = None
            LOGS.error(f"Error getting media: {e}")
    response = f"""*I'm alive!*

💝 *Version:* {VERSION}
💖 *Uptime:* {parse_ms((time.time() - START_TIME) * 1000)}
🐍 *Python:* {version_info.major}.{version_info.minor}.{version_info.micro}
📦 *Platform:* {platform}"""
    await message.reply_text(response, media_info=media)


@command("help")
async def list_commands(message: Message):
    """List all available commands. Use `help <plugin>` to list commands for a specific plugin."""
    try:
        param = message.message.split(maxsplit=1)[1]
        if PLUGINS_MENU.get(param):
            response = f"*Here are the available commands for {param}*:\n\n"
            for command in PLUGINS_MENU[param]:
                response += f"- `{command}`\n"
                if HELP_MENU.get(command):
                    response += f"  - {HELP_MENU[command]}\n"
            await message.edit_text(response.strip())
            return
    except IndexError:
        pass
    response = "Here are the available plugins:"
    for plugin in PLUGINS_MENU:
        response += f"\n\n*{plugin}*"
        for command in PLUGINS_MENU[plugin]:
            response += f"\n- `{command}`"
    await message.edit_text(response)


#    buttons = [InlineKeyboardButton(bts, callback_data=f"plugin_help_{bts}") for bts in PLUGINS_MENU]
#    await message.edit_text("Here are the available plugins:", buttons=buttons)


@command("json")
async def json_command(message: Message):
    """Get the JSON data of a message."""
    replied = (await message.get_replied_message()) or message
    data = replied.to_json()
    await message.edit_text(json.dumps(data, indent=4))


@command("id")
async def id_command(message: Message):
    replied = await message.get_replied_message()
    response = ""
    if message.community_id:
        print(message.community_id)
        response += f"👥 *Community ID:* <copy>{message.community_id}</copy>\n"
        if message.group_id:
            response += f"👥 *Group ID:* <copy>{message.group_id}`</copy>\n"
        elif message.channel_id:
            response += f"👥 *Channel ID:* <copy>{message.channel_id}</copy>\n"
    if replied:
        response += f"📄 *Replied to Message ID:* `{replied.id}`\n"
        response += f"👤 *User ID:* `{replied.user_id}`\n"
    else:
        response += f"📄 *Message ID:* `{message.id}`\n"
    await message.edit_text(response.strip())


@command("logs")
async def on_logs(message: Message):
    """Get the logs of the bot."""
    thumb = Config.get("VAR_THUMB") or Config.get("VAR_ALIVE_MEDIA")
    if thumb:
        try:
            media = await message.app.get_media(int(thumb))
            thumb = media.thumbnail_url
        except Exception as e:
            LOGS.error(f"Error getting media: {e}")
    msg = await message.reply_document(
        message="Here are the logs of the bot:", document=LOG_PATH, thumb=thumb
    )
    await message.delete()


@command("restart")
async def on_restart(message: Message):
    """Restart the bot."""
    await message.edit_text("Restarting...")
    os.execl(sys.executable, sys.executable, sys.arg[-1])


add_doc("Basic", ["ping", "alive", "help", "json", "id", "logs"])
