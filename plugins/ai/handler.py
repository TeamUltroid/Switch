from .. import *
from .grok import performAction, make_request


@command("ai", handler=":")
async def on_ai_message(m: Message):
    try:
        command = m.message.split(" ", 1)[1]
    except IndexError:
        await m.reply_text("Invalid usage of command.")
        return
    response = make_request(command)

    m = await m.edit_text(f"⚡ *Processing...*")

    action_response = {}
    for action in response.get("actions", []):
        try:
            call_response = await performAction(action, m, action_response)
            if call_response and isinstance(call_response, dict):
                action_response.update(call_response)
        except Exception as er:
            LOGS.exception(er)
            await m.edit_text(f"ERROR: {er}")
            return

    await m.edit_text(
        f"🪄 *Query*: {command}\n\n🌟 *Response*: {response['message']}"
    )
