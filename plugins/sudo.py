from . import command, Message, add_doc


@command("addsudo")
async def on_addsudo(message: Message):
    pass


@command("deletesudo")
async def on_deletesudo(message: Message):
    pass


@command("listsudo")
async def on_listsudo(message: Message):
    pass


add_doc(
    "Sudo", ["addsudo", "deletesudo", "listsudo"]
)