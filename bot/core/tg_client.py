from pyrogram import Client, enums
from asyncio import Lock, gather
from inspect import signature
import os

from .. import LOGGER
from .config_manager import Config


# ======================
# SESSION CONFIGURATION
# ======================
SESSION_DIR = "sessions"
os.makedirs(SESSION_DIR, exist_ok=True)


class TgClient:
    _lock = Lock()
    _hlock = Lock()

    bot = None
    user = None
    helper_bots = {}
    helper_loads = {}

    BNAME = ""
    ID = 0
    IS_PREMIUM_USER = False
    MAX_SPLIT_SIZE = 2097152000

    # ======================
    # BASE CLIENT FACTORY
    # ======================
    @classmethod
    def wztgClient(cls, *args, **kwargs):
        kwargs["api_id"] = Config.TELEGRAM_API
        kwargs["api_hash"] = Config.TELEGRAM_HASH
        kwargs["proxy"] = Config.TG_PROXY
        kwargs["parse_mode"] = enums.ParseMode.HTML

        # ✅ STORE SESSION FILES
        kwargs["workdir"] = SESSION_DIR

        for param, value in {
            "max_concurrent_transmissions": 100,
            "skip_updates": False,
        }.items():
            if param in signature(Client.__init__).parameters:
                kwargs[param] = value

        return Client(*args, **kwargs)

    # ======================
    # HELPER BOT STARTER
    # ======================
    @classmethod
    async def start_hclient(cls, no, b_token):
        try:
            hbot = await cls.wztgClient(
                f"WZ-HBot{no}",
                bot_token=b_token,
                no_updates=True,
            ).start()

            LOGGER.info(f"Helper Bot [@{hbot.me.username}] Started!")
            cls.helper_bots[no] = hbot
            cls.helper_loads[no] = 0

        except Exception as e:
            LOGGER.error(f"Failed to start helper bot {no}. {e}")
            cls.helper_bots.pop(no, None)

    @classmethod
    async def start_helper_bots(cls):
        if not Config.HELPER_TOKENS:
            return

        LOGGER.info("Generating helper clients from HELPER_TOKENS")
        async with cls._hlock:
            await gather(
                *(
                    cls.start_hclient(no, token)
                    for no, token in enumerate(
                        Config.HELPER_TOKENS.split(), start=1
                    )
                )
            )

    # ======================
    # MAIN BOT
    # ======================
    @classmethod
    async def start_bot(cls):
        LOGGER.info("Generating client from BOT_TOKEN")

        cls.ID = Config.BOT_TOKEN.split(":", 1)[0]
        cls.bot = cls.wztgClient(
            f"WZ-Bot{cls.ID}",
            bot_token=Config.BOT_TOKEN,
        )

        await cls.bot.start()
        cls.BNAME = cls.bot.me.username

        LOGGER.info(f"WZ Bot : [@{cls.BNAME}] Started!")

    # ======================
    # USER ACCOUNT
    # ======================
    @classmethod
    async def start_user(cls):
        if not Config.USER_SESSION_STRING:
            return

        LOGGER.info("Generating client from USER_SESSION_STRING")

        try:
            cls.user = cls.wztgClient(
                "WZ-User",
                session_string=Config.USER_SESSION_STRING,
                sleep_threshold=60,
                no_updates=True,
            )

            await cls.user.start()
            cls.IS_PREMIUM_USER = cls.user.me.is_premium

            if cls.IS_PREMIUM_USER:
                cls.MAX_SPLIT_SIZE = 4194304000

            uname = cls.user.me.username or cls.user.me.first_name
            LOGGER.info(f"WZ User : [{uname}] Started!")

        except Exception as e:
            LOGGER.error(f"Failed to start USER client. {e}")
            cls.user = None
            cls.IS_PREMIUM_USER = False

    # ======================
    # STOP ALL CLIENTS
    # ======================
    @classmethod
    async def stop(cls):
        async with cls._lock:
            if cls.bot:
                await cls.bot.stop()
                cls.bot = None

            if cls.user:
                await cls.user.stop()
                cls.user = None

            if cls.helper_bots:
                await gather(*(h.stop() for h in cls.helper_bots.values()))
                cls.helper_bots.clear()

            LOGGER.info("All Client(s) stopped")

    # ======================
    # RESTART ALL CLIENTS
    # ======================
    @classmethod
    async def reload(cls):
        async with cls._lock:
            if cls.bot:
                await cls.bot.restart()

            if cls.user:
                await cls.user.restart()

            if cls.helper_bots:
                await gather(*(h.restart() for h in cls.helper_bots.values()))

            LOGGER.info("All Client(s) restarted")
