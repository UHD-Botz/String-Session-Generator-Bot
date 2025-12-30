from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN


class Bot(Client):
    def __init__(self):
        if not all([API_ID, API_HASH, BOT_TOKEN]):
            raise ValueError("❌ API_ID, API_HASH, or BOT_TOKEN is missing!")

        super().__init__(
            name="uhd_string_session_bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="UHDBots"),
            workers=150,
            sleep_threshold=10
        )

    async def start(self):
        await super().start()
        me = await self.get_me()

        username = f"@{me.username}" if me.username else "(no username)"
        print(f"🤖 Bot Started as {me.first_name} {username}")
        print("🚀 Powered By @UHDBots")

    async def stop(self, *args):
        await super().stop()
        print("🛑 Bot Stopped. Bye!")


if __name__ == "__main__":
    Bot().run()
