from functions.tasks import fetch
from io import BytesIO
from . import command, Message


@command("ghuser")
async def on_get_user(message: Message):
    try:
        username = message.message.split()[1]
    except IndexError:
        await message.edit_text("Invalid usage of command.")
        return
    url = f"https://api.github.com/users/{username}"
    response = await fetch(url)
    if response.status_code == 200:
        user_data = response.json()
        response = f"👤 *User Info*\n\n"
        response += f"  *Name:* {user_data['name']}\n"
        response += f"  *Bio:* {user_data['bio']}\n"
        response += f"  *Followers:* {user_data['followers']} | *Following: {user_data['following']}*\n"
        if user_data.get("location"):
            response += f"  *Location:* {user_data['location']}\n"
        if user_data.get("email"):
            response += f"  *Email:* {user_data['email']}\n"
        if user_data.get("twitter_username"):
            response += f"  *Twitter:* @{user_data['twitter_username']}\n"
        file = user_data.get("avatar_url")
        if file:
            file = BytesIO((await fetch(file)).content)
            file.name = "avatar.png"

        await message.reply_media(
            file,
            response.strip(),
        )
        await message.delete()
    else:
        await message.edit_text("❌ Failed to fetch user data from GitHub")
