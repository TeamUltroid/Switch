from . import command, Message, add_doc


@command("addsudo")
async def on_addsudo(message: Message):
    pass


@command("delsudo")
async def on_deletesudo(message: Message):
    pass


@command("listsudo")
async def on_listsudo(message: Message):
    pass


add_doc(
    "Sudo", ["addsudo", "delsudo", "listsudo"]
)