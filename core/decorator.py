import re
from core.constants import HELP_MENU
from client import user
from config import Config
from swibots import MessageHandler
from swibots import BotContext, MessageEvent


def compile_pattern(data, hndlr):
    if isinstance(data, re.Pattern):
        data = data.pattern
    if data.startswith("^"):
        data = data[1:]
    if data.startswith("."):
        data = data[1:]
    return re.compile("\\" + hndlr + data)


def command(pattern,
            community_only: bool = False,
            handler=None):

    def function(func):

        async def decorator(ctx: BotContext[MessageEvent]):
            command_handler = handler or Config.get("HANDLER", ".")
            m = ctx.event.message
            re_pattern = compile_pattern(pattern, command_handler)
            matched = re.match(re_pattern, m.message)
            if matched:
                if community_only and m.receiver_id:
                    await m.edit_text("This command is only available in communities.")
                    return
                await func(m)

        if func.__doc__:
            HELP_MENU[pattern] = func.__doc__
        user.add_handler(MessageHandler(decorator, outgoing=True))

    return function
