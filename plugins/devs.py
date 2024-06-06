import asyncio
import io
import os
import random
import re
import sys
import traceback
from . import command, Message, add_doc


async def aexec(code, message):
    exec(f"async def __aexec(message): " + "".join(f"\n {l}" for l in code.split("\n")))
    return await locals()["__aexec"](message)


async def stream_response(code, response, ctx):
    old_text = ""
    while True:
        # Read a chunk of data from the response
        chunk = await response.read(2048)
        if not chunk:
            break
        # Process the chunk of data
        # ...
        # Edit the response in the chat
        chunk = chunk.decode("utf-8")
        old_text = old_text + chunk
        # check if the message is too long send in new message
        await ctx.edit_text("Bash: <copy>{}</copy>\n<copy>{}</copy>".format(code, old_text))
        # Wait for a short interval before reading the next chunk
        await asyncio.sleep(0.7)


@command("eval")
async def on_eval(message: Message):
    hash = random.randint(100, 999)
    try:
        code = message.message.split(" ", 1)[1]
    except IndexError:
        await message.edit_text("Invalid usage of command.")
        return
    process_text = await message.edit_text("Processing...")
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None
    try:
        await aexec(code, message)
    except Exception as e:
        exc = traceback.format_exc()

    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"
    response = f"🧑‍💻 *Eval*\n\n"
    response += f"*Code*: <copy>{code}</copy>\n\n"
    response += f"*Response*: <copy>{evaluation}</copy>"
    if len(response) > 4096:
        with open(f"output{hash}.txt", "w", encoding="utf-8") as file:
            file.write(response)
        try:
            await process_text.delete()
        except Exception:
            pass
        await message.reply_document(f"output{hash}.txt")
        os.remove(f"output{hash}.txt")
    else:
        await message.edit_text(response)


@command("bash")
async def on_bash(message: Message):
    hash = random.randint(1000, 9999)
    match = re.search(r'\.(.*)', message.message)
    command_and_args = match.group(1)  # get the part of the string after the dot
    parts = command_and_args.split()  # split into individual parts
    command = [part for part in parts if not part.startswith('-')][0]  # the first part that doesn't start with - is the command
    args = [part for part in parts if part.startswith('-')]  # the rest that start with - are the arguments
    code = ' '.join([part for part in parts if not part.startswith('-') and part!= command])
    try:
        process = await asyncio.create_subprocess_shell(
            code,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        msg = await message.edit_text("Running...")
        if "-s" in args:
            # Stream the stdout response
            await stream_response(code, process.stdout, msg)
            # Stream the stderr response
            await stream_response(code, process.stderr, msg)
            # Wait for the process to complete
            await process.wait()
        else:
            stdout, stderr = await process.communicate()
            output = stdout.decode().strip() + stderr.decode().strip()
            if len(output) > 4096:
                with open(f"output{hash}.txt", "w", encoding="utf-8") as file:
                    file.write("Stdout: {}\n\nStderr: {}".format(stdout.decode(), stderr.decode()))
                try:
                    await process.kill()
                except Exception:
                    pass
                await msg.reply_document(f"output{hash}.txt", "Bash: <copy>{}</copy>".format(code))
                os.remove(f"output{hash}.txt")
                try:
                    await msg.delete()
                except Exception:
                    pass
            else:
                await msg.edit_text("Bash: <copy>{}</copy>\n\nStdout: <copy>{}</copy>\n\nStderr: {}".format(code, stdout.decode().strip(), stderr.decode().strip()))
    except Exception as e:
        print(traceback.format_exc())
        await msg.edit_text(f"Error: {e}")


add_doc("Devs", ["eval", "bash"])
