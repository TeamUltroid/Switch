from . import command, Message, add_doc
from functions.tasks import run_async

@run_async
def ytsearch(query):
    from youtubesearchpython import VideosSearch
    
    search = VideosSearch(query, limit=10).result()
    return search['result']


@command("ytsearch")
async def on_ytsearch(message: Message):
    try:
        query = message.message.split(" ", 1)[1]
    except IndexError:
        await message.edit_text("Invalid usage of command.")
        return
    results = await ytsearch(query)
    response = f"🌟 *Search results for:* `{query}`\n\n"
    for result in results[:5]:
        response += f"🔗 [{result['title']}]({result['link']})\n"
        if result.get("descriptionSnippet"):
            response += f"    __{result['descriptionSnippet'][0]['text']}__\n"
        response += f"    *Published on:* __{result['publishedTime']}__\n\n"
    await message.edit_text(response.strip())

add_doc("Youtube", ["ytsearch"])