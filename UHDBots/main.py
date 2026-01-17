from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import (
    ApiIdInvalidError,
    PhoneNumberInvalidError,
    PhoneCodeInvalidError,
    PhoneCodeExpiredError,
    SessionPasswordNeededError,
    PasswordHashInvalidError
)

from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message
)
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid
)

from asyncio.exceptions import TimeoutError


# ───────────────── BUTTONS ───────────────── #

ask_ques = "**» ▷ Choose the session type you want to generate:**"

buttons_ques = [
    [
        InlineKeyboardButton("🔥 Pyrogram v2 (User)", callback_data="pyrogram_v2"),
        InlineKeyboardButton("🤖 Pyrogram v2 (Bot)", callback_data="pyrogram_v2_bot"),
    ],
    [
        InlineKeyboardButton("📡 Telethon (User)", callback_data="telethon"),
        InlineKeyboardButton("🤖 Telethon (Bot)", callback_data="telethon_bot"),
    ],
    [
        InlineKeyboardButton("❌ Close", callback_data="close")
    ]
]

gen_button = [
    [InlineKeyboardButton("🔁 Generate Again", callback_data="generate")]
]


@Client.on_message(filters.private & filters.command(["gen"]))
async def main(_, msg: Message):
    await msg.reply(
        ask_ques,
        reply_markup=InlineKeyboardMarkup(buttons_ques)
    )


# ───────────────── SESSION GENERATOR ───────────────── #

async def generate_session(
    bot: Client,
    msg: Message,
    telethon: bool = False,
    is_bot: bool = False
):
    # Session name
    if telethon:
        session_type = "TELETHON"
    else:
        session_type = "PYROGRAM v2"

    if is_bot:
        session_type += " BOT"

    await msg.reply(f"🚀 Starting **{session_type}** session generator...")

    user_id = msg.chat.id

    # API ID
    api_id_msg = await bot.ask(
        user_id,
        "📌 Send your **API_ID**",
        filters=filters.text
    )
    if await cancelled(api_id_msg):
        return

    try:
        api_id = int(api_id_msg.text)
    except ValueError:
        await api_id_msg.reply(
            "❌ API_ID must be a number.",
            reply_markup=InlineKeyboardMarkup(gen_button)
        )
        return

    # API HASH
    api_hash_msg = await bot.ask(
        user_id,
        "📌 Send your **API_HASH**",
        filters=filters.text
    )
    if await cancelled(api_hash_msg):
        return

    api_hash = api_hash_msg.text.strip()

    # Phone or Bot Token
    if is_bot:
        ask_text = "🤖 Send your **BOT TOKEN**"
    else:
        ask_text = (
            "📱 Send your **PHONE NUMBER** with country code\n"
            "Example: `+911234567890`"
        )

    auth_msg = await bot.ask(user_id, ask_text, filters=filters.text)
    if await cancelled(auth_msg):
        return

    auth_value = auth_msg.text.strip()

    # ─────────── CLIENT CREATION ─────────── #

    if telethon:
        client = TelegramClient(
            StringSession(),
            api_id,
            api_hash
        )
        await client.connect()
    else:
        client = Client(
            name="session",
            api_id=api_id,
            api_hash=api_hash,
            bot_token=auth_value if is_bot else None,
            in_memory=True
        )
        await client.connect()

    # ─────────── LOGIN FLOW ─────────── #

    try:
        if not is_bot:
            if telethon:
                await client.send_code_request(auth_value)
            else:
                code = await client.send_code(auth_value)

            otp_msg = await bot.ask(
                user_id,
                "🔐 Send the **OTP** (space separated)\nExample: `1 2 3 4 5`",
                filters=filters.text,
                timeout=600
            )
            if await cancelled(otp_msg):
                return

            otp = otp_msg.text.replace(" ", "")

            try:
                if telethon:
                    await client.sign_in(auth_value, otp)
                else:
                    await client.sign_in(
                        auth_value,
                        code.phone_code_hash,
                        otp
                    )

            except (SessionPasswordNeeded, SessionPasswordNeededError):
                pwd_msg = await bot.ask(
                    user_id,
                    "🔑 Enter your **2-Step Verification Password**",
                    filters=filters.text,
                    timeout=300
                )
                if telethon:
                    await client.sign_in(password=pwd_msg.text)
                else:
                    await client.check_password(password=pwd_msg.text)

        else:
            if telethon:
                await client.start(bot_token=auth_value)
            else:
                await client.sign_in_bot(auth_value)

    except (
        ApiIdInvalid,
        ApiIdInvalidError,
        PhoneNumberInvalid,
        PhoneNumberInvalidError,
        PhoneCodeInvalid,
        PhoneCodeInvalidError,
        PhoneCodeExpired,
        PhoneCodeExpiredError,
        PasswordHashInvalid,
        PasswordHashInvalidError
    ):
        await msg.reply(
            "❌ Authentication failed. Please try again.",
            reply_markup=InlineKeyboardMarkup(gen_button)
        )
        await client.disconnect()
        return

    # ─────────── EXPORT SESSION ─────────── #

    if telethon:
        string_session = client.session.save()
    else:
        string_session = await client.export_session_string()

    session_text = (
        f"🔐 **Your {session_type} String Session**\n\n"
        f"`{string_session}`\n\n"
        "⚠️ **DO NOT SHARE THIS STRING WITH ANYONE**"
    )

    try:
        await bot.send_message(user_id, session_text)
    except Exception:
        pass

    await client.disconnect()

    await bot.send_message(
        user_id,
        f"✅ **{session_type} session generated successfully!**\n"
        "📁 Check your saved messages.",
        reply_markup=InlineKeyboardMarkup(gen_button)
    )


# ───────────────── CANCEL HANDLER ───────────────── #

async def cancelled(msg: Message):
    if msg.text and "/cancel" in msg.text.lower():
        await msg.reply(
            "❌ Session generation cancelled.",
            reply_markup=InlineKeyboardMarkup(gen_button)
        )
        return True
    return False
