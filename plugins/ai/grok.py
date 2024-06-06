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
You are a powerful AI assistant on community messaging platform named Switch, Switch is community first platform, with games, mini-apps and lot more for everyone. You are integrated to the userbot and can perform actions based on the user's behalf and help them in conveniently perform their tasks.

Here are the set of actions [that can be only performed]:
<actions>
{actions}
</actions>

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

<break />
# Using response of previous actions
use 'result[n].attribute' to access any value from previous response,
for example, to access output of response from first message
{
    "message": "copying previous message",
    "actions": [
{"action": "create_channel",
"name": "New channel", "icon": "❣️"},
{
        "action": "send_message",
        "message": "result[0].channelId"
    }]
}

<break />
Every response should be json parsable and never include any other extra text.
<break />
Every action you choose, gets executed in the order you provide them.
be careful with every action that you choose, as they can result in serious consequences."""

print(SYSTEM_MESSAGE)
messageBox = [
    {"role": "system", "content": SYSTEM_MESSAGE},
]


async def make_request(query, m: Message = None):
    if len(messageBox) > 200:
        messageBox.pop(1)
    #    print(m)
    if m:
        if m.receiver_id:
            query += f"---\nChat user id: {m.receiver_id}\nUser's Name: {m.user.name}"
        else:
            community = await user.get_community(m.community_id)
            query += f"""---
    Current community name: {community.name}
    Current community id: {community.id}
    """
    messageBox.append({"role": "user", "content": query})
    response = (
        client.chat.completions.create(
            messages=messageBox,
            model=MODEL,
            temperature=1.5,
            max_tokens=2000,
            seed=5555,
        )
        .choices[0]
        .message.content
    )
    print(response)

    try:
        json_response = json.loads(response)
        messageBox.append({"role": "user", "content": str(json_response)})
        return json_response
    except Exception as er:
        print(response)
        return {"error": "Unable to get response"}


async def performAction(action, m: Message, previousResponse: dict):
    actionName = action["action"]
    personal_chat = m.personal_chat

    if actions.get(actionName):
        for x, y in actions[actionName]["params"].items():
            if not action.get(x) and "[optional]" not in y:
                return {"error": f"Missing parameter {x}"}

    for x, y in action.items():
        if x != "action":
            if y.startswith("."):
                attributeName = y[1:]
                action[x] = previousResponse.get(attributeName)
            if y.startswith("result["):
                try:
                    index = int(y.split("[")[1].split("]")[0])
                    attributeName = y.split(".")[-1]
                    action[x] = previousResponse.get(index, {}).get(attributeName)
                except Exception as er:
                    print(er)
    print(action)

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
    return response
