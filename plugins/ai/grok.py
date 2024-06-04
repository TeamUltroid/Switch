import json
from config import Config
from groq import Client
from swibots import Message
from client import user
from swibots import Channel, Group

MODEL = Config.get("GROQ_MODEL", "llama3-70b-8192")

client = Client(
    api_key=Config.get("GROQ_API_KEY"),
)
ACTIONS_PATH = "plugins/ai/actions.json"

with open(ACTIONS_PATH, "r") as f:
    actions = json.load(f)

SYSTEM_MESSAGE = f"""
You are a powerful AI assistant on community messaging platform named Switch, Switch is community  first platform, with games, mini-apps and lot more for everyone. You are integrated to the userbot and can perform actions based on the user's behalf and help them in conveniently perform their tasks.

Here are the set of actions [that can be only performed]:
{actions}

for any response, return a json response, and  use the same key names,
add a response message for the user, informing of the action
Always return a valid json response, and use actions only specified!
If something user is asking is not possible or related to spam, return an error message saying you dont understand them
"""
SYSTEM_MESSAGE += """
Output response example is given below:
{
"message": "This is a example response",
"actions": [
{"action": "create_channel", "name": "New channel", "icon": "🔗"}
]
}

use '.attribute' to access any value from previous response,
for example,
{
    "message": "copying previous message",
    "actions": [{
        "action": "send_message",
        "message": ".message"
    }]
}
"""

messageBox = [
    {"role": "system", "content": SYSTEM_MESSAGE},
]


def make_request(query):
    if len(messageBox) > 20:
        messageBox.pop(1)
    messageBox.append({"role": "user", "content": query})
    response = (
        client.chat.completions.create(messages=messageBox, model=MODEL)
        .choices[0]
        .message.content
    )
    print(response)

    try:
        return json.loads(response)
    except Exception as er:
        print(response)
        return {"error": "Unable to get response"}


async def performAction(action, m: Message, previousResponse: dict):
    actionName = action["action"]
    personal_chat = m.personal_chat
    print(action, 69)

    if actions.get(actionName):
        for x, y in actions[actionName]["params"].items():
            if not action.get(x) and "[optional]" not in y:
                return {"error": f"Missing parameter {x}"}

    for x, y in action.items():
        if x != "action" and y.startswith("."):
            attributeName = y[1:]
            action[x] = previousResponse.get(attributeName)

    print(77, action)

    if actionName == "create_channel":
        if personal_chat:
            return await m.edit("This action can only be performed in a group chat")
        response = await user.create_channel(
            channel=Channel(
                name=action["name"],
                icon=action["icon"],
                community_id=m.community_id,
                is_public=True,
                enabled_public=True,
            )
        )
        response = {"channelId": response}
    elif actionName == "create_group":
        response = await user.create_group(
            group=Group(
                name=action["name"],
                icon=action["icon"],
                is_public=True,
                enabled_public=True,
            )
        )
        response = {"groupId": response}
    elif actionName == "send_message":
        if action.get("channel_id") or action.get("group_id"):
            community = None
            if action.get("channel_id"):
                community = (await user.get_channel(action["channel_id"])).community_id
            elif action.get("group_id"):
                community = (await user.get_group(action["group_id"])).community_id
            else:
                return {"error": "Missing channel_id or group_id"}

            response = await user.send_message(
                channel_id=action.get("channel_id", None),
                group_id=action.get("group_id", None),
                message=action.get("message", ""),
                community_id=community,
            )
        else:
            response = await m.send(action["message"])
        response = {"messageId": response.id}
    else:
        return

    print(response)
    return response
