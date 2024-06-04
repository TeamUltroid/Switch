from . import command, Message, add_doc

@command("eval")
async def on_eval(message: Message):
    try:
        code = message.message.split(" ", 1)[1]
    except IndexError:
        await message.edit_text("Invalid usage of command.")
        return
    try:
        exec(f"async def __ex(message: Message): return {code}")
        response = await locals()["__ex"](message)
    except Exception as e:
        response = str(e)
    response = f"🧑‍💻 *Eval*\n\n"
    response += f"*Code*: `{code}`\n\n"
    response += f"*Response*: `{response}`"
    await message.edit_text(response)


@command("exec")
async def on_exec(message: Message):
    try:
        code = message.message.split(" ", 1)[1]
    except IndexError:
        await message.edit_text("Invalid usage of command.")
        return
    try:
        exec(code)
        response = "Code executed successfully."
    except Exception as e:
        response = str(e)
    await message.edit_text(f"```{response}```")

add_doc("Devs", ["eval", "exec"])