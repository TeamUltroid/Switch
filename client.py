import logging
from config import BOT_NAME

LOG_PATH = f"{BOT_NAME}.log"


logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler(LOG_PATH, mode="w", encoding="utf8"),
        logging.StreamHandler(),
    ],
)
from config import LOGS, Config
from swibots import Client

user_token = Config.get("USER_TOKEN")
if not user_token:
    LOGS.error("Please provide your user token in the config.py file.")
    exit(1)


class UClient(Client):

    def __init__(self, user_token, **kwargs):
        super().__init__(user_token, **kwargs)


user: UClient = UClient(user_token, plugins=dict(root="plugins"))


TG_BOT_TOKEN = Config.get("TG_BOT_TOKEN")

if TG_BOT_TOKEN:
    from telethon import TelegramClient

    tg_bot: TelegramClient = TelegramClient(
        "plugins/telegram/bot",
        api_id=Config.get("TG_API_ID"),
        api_hash=Config.get("TG_API_HASH"),
    )
    LOGS.info("Starting telegram bot client")

    tg_bot.start(bot_token=TG_BOT_TOKEN)
else:
    tg_bot = None
