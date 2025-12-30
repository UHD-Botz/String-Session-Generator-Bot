import config
from telethon import TelegramClient
from telethon.sessions import StringSession
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import FloodWait
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid
)
from telethon.errors import (
    ApiIdInvalidError,
    PhoneNumberInvalidError,
    PhoneCodeInvalidError,
    PhoneCodeExpiredError,
    SessionPasswordNeededError,
    PasswordHashInvalidError
)
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from asyncio.exceptions import TimeoutError
from UHDBots.db import db


# ===============================
# REQUIRED FOR callbacks.py
# ===============================
ask_ques = "**» ▷ Choose the string type you want:**"

buttons_ques = [
    [
        InlineKeyboardButton("𝗧𝗘𝗟𝗘𝗧𝗛𝗢𝗡", callback_data="telethon"),
        InlineKeyboardButton("𝗣𝗬𝗥𝗢𝗚𝗥𝗔𝗠", callback_data="pyrogram")
    ],
    [
        InlineKeyboardButton("𝗣𝗬𝗥𝗢𝗚𝗥𝗔𝗠 𝗕𝗢𝗧", callback_data="pyrogram_bot"),
        InlineKeyboardButton("𝗧𝗘𝗟𝗘𝗧𝗛𝗢𝗡 𝗕𝗢𝗧", callback_data="telethon_bot")
    ]
]

GEN_BTN = [[InlineKeyboardButton("⚡ Generate String ⚡", callback_data="generate")]]


@Client.on_message(filters.private & filters.command(["generate", "gen", "string", "str"]))
async def generate_cmd(_, msg: Message):
    await msg.reply(
        ask_ques,
        reply_markup=InlineKeyboardMarkup(buttons_ques)
    )


async def generate_session(bot: Client, msg: Message, telethon=False, is_bot=False):
    user_id = msg.from_user.id

    if not await db.is_user_exist(user_id):
        await db.add_user(user_id, msg.from_user.first_name)

    # FORCE SUB CHECK
    if config.F_SUB:
        try:
            await bot.get_chat_member(int(config.F_SUB), user_id)
        except UserNotParticipant:
            invite = await bot.create_chat_invite_link(int(config.F_SUB))
            await msg.reply(
                "**⚠️ Access Denied! Join the channel first.**",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🍿 Join Channel 🍿", url=invite.invite_link)],
                    [InlineKeyboardButton("🍀 Check Again 🍀", callback_data="chk")]
                ])
            )
            return

    ty = "TELETHON" if telethon else "PYROGRAM"
    if is_bot:
        ty += " BOT"

    await msg.reply(f"» Starting **{ty}** session generator...")

    # API ID / HASH
    api_id_msg = await bot.ask(user_id, "Send **API_ID** or `/skip`", filters=filters.text)
    if await cancelled(api_id_msg):
        return

    if api_id_msg.text == "/skip":
        api_id = config.API_ID
        api_hash = config.API_HASH
    else:
        try:
            api_id = int(api_id_msg.text)
        except ValueError:
            await msg.reply("❌ API_ID must be integer", reply_markup=InlineKeyboardMarkup(GEN_BTN))
            return

        api_hash_msg = await bot.ask(user_id, "Send **API_HASH**", filters=filters.text)
        if await cancelled(api_hash_msg):
            return

        api_hash = api_hash_msg.text.strip()

    # PHONE / BOT TOKEN
    prompt = "Send **Phone Number** with country code" if not is_bot else "Send **Bot Token**"
    phone_msg = await bot.ask(user_id, prompt, filters=filters.text)
    if await cancelled(phone_msg):
        return

    phone = phone_msg.text.strip()

    client = None
    try:
        if telethon:
            client = TelegramClient(StringSession(), api_id, api_hash)
            await client.connect()
        else:
            client = Client(
                name="gen",
                api_id=api_id,
                api_hash=api_hash,
                bot_token=phone if is_bot else None,
                in_memory=True
            )
            await client.start()

        if not is_bot:
            if telethon:
                await client.send_code_request(phone)
            else:
                await client.send_code(phone)

            code_msg = await bot.ask(
                user_id,
                "Send **OTP** (Example: `1 2 3 4 5`)",
                filters=filters.text,
                timeout=600
            )
            if await cancelled(code_msg):
                return

            code = code_msg.text.replace(" ", "")

            try:
                if telethon:
                    await client.sign_in(phone, code)
                else:
                    await client.sign_in(phone, code)
            except SessionPasswordNeeded:
                pwd = await bot.ask(user_id, "Send **2FA Password**", timeout=300)
                if telethon:
                    await client.sign_in(password=pwd.text)
                else:
                    await client.check_password(pwd.text)

        # EXPORT STRING
        string = client.session.save() if telethon else await client.export_session_string()

        await bot.send_message(
            user_id,
            f"**Your {ty} String Session:**\n\n`{string}`\n\n"
            "**⚠️ Never share this with anyone!**"
        )

    except FloodWait as e:
        await msg.reply(f"⏳ FloodWait {e.x}s. Try again later.")
    except (
        ApiIdInvalid, ApiIdInvalidError,
        PhoneNumberInvalid, PhoneNumberInvalidError,
        PhoneCodeInvalid, PhoneCodeInvalidError,
        PhoneCodeExpired, PhoneCodeExpiredError,
        PasswordHashInvalid, PasswordHashInvalidError
    ):
        await msg.reply("❌ Invalid credentials. Try again.", reply_markup=InlineKeyboardMarkup(GEN_BTN))
    except TimeoutError:
        await msg.reply("⌛ Time expired. Start again.", reply_markup=InlineKeyboardMarkup(GEN_BTN))
    finally:
        try:
            if client:
                await client.disconnect()
        except:
            pass


async def cancelled(msg: Message):
    if msg.text.startswith("/"):
        await msg.reply("❌ Process cancelled.", reply_markup=InlineKeyboardMarkup(GEN_BTN))
        return True
    return False
