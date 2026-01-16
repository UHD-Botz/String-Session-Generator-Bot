# Authored By Certified Coders — v1.2 (2025-11-14)
import os, json, logging
from datetime import datetime, timezone
from asyncio.exceptions import TimeoutError

import config
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from telethon import TelegramClient
from telethon.sessions import StringSession
from StringGen.utils import ask

from pyrogram.errors import (
    ApiIdInvalid, PhoneNumberInvalid, PhoneCodeInvalid, PhoneCodeExpired,
    SessionPasswordNeeded, PasswordHashInvalid,
    ApiIdInvalid as ApiIdInvalid1, PhoneNumberInvalid as PhoneNumberInvalid1,
    PhoneCodeInvalid as PhoneCodeInvalid1, PhoneCodeExpired as PhoneCodeExpired1,
    SessionPasswordNeeded as SessionPasswordNeeded1, PasswordHashInvalid as PasswordHashInvalid1,
)
from telethon.errors import (
    ApiIdInvalidError, PhoneNumberInvalidError, PhoneCodeInvalidError,
    PhoneCodeExpiredError, SessionPasswordNeededError, PasswordHashInvalidError,
    FloodWaitError, AuthRestartError,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

os.makedirs("StringsHolder", exist_ok=True)

ASK_QUES = "**☞︎︎︎ ᴄʜᴏᴏꜱᴇ ᴀ ꜱᴇꜱꜱɪᴏɴ ᴛʏᴘᴇ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ 𖤍 ✔️**"
BUTTONS_QUES = [
    [
        InlineKeyboardButton("ᴘʏʀᴏɢʀᴀᴍ ᴠ1", callback_data="pyrogram_v1"),
        InlineKeyboardButton("ᴘʏʀᴏɢʀᴀᴍ ᴠ2", callback_data="pyrogram_v2"),
    ],
    [InlineKeyboardButton("ᴛᴇʟᴇᴛʜᴏɴ", callback_data="telethon")],
    [
        InlineKeyboardButton("ᴘʏʀᴏɢʀᴀᴍ ʙᴏᴛ", callback_data="pyrogram_bot"),
        InlineKeyboardButton("ᴛᴇʟᴇᴛʜᴏɴ ʙᴏᴛ", callback_data="telethon_bot"),
    ],
]
GEN_BUTTON = [[InlineKeyboardButton("ɢᴇɴᴇʀᴀᴛᴇ ꜱᴇꜱꜱɪᴏɴ 𖤍", callback_data="generate")]]

async def ask_or_cancel(bot: Client, uid: int, prompt: str, *, timeout: int | None = None) -> str | None:
    try:
        m = await ask(bot, uid, prompt, timeout=timeout)
    except TimeoutError:
        raise TimeoutError("ᴛɪᴍᴇᴏᴜᴛ – ɴᴏ ʀᴇᴘʟʏ ғᴏʀ ᴀ ᴡʜɪʟᴇ")

    tx = m.text.strip()
    if tx in ("/cancel", "/restart"):
        await bot.send_message(uid,
            "» ᴄᴀɴᴄᴇʟʟᴇᴅ." if tx == "/cancel" else "» ʀᴇꜱᴛᴀʀᴛɪɴɢ ʙᴏᴛ...",
            reply_markup=InlineKeyboardMarkup(GEN_BUTTON),
        )
        return None
    return tx

def save_to_cache(uid: int, string_: str, meta: dict) -> None:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = f"StringsHolder/{uid}_{ts}"
    with open(base + "_session.txt", "w") as f:
        f.write(string_)
    with open(base + "_info.json", "w") as f:
        json.dump(meta, f, indent=2)

def readable_error(exc: Exception) -> str:
    mapping = {
        (ApiIdInvalid, ApiIdInvalid1, ApiIdInvalidError): "ɪɴᴠᴀʟɪᴅ **ᴀᴘɪ ɪᴅ/ʜᴀꜱʜ**.",
        (PhoneNumberInvalid, PhoneNumberInvalid1, PhoneNumberInvalidError): "ɪɴᴠᴀʟɪᴅ **ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ**.",
        (PhoneCodeInvalid, PhoneCodeInvalid1, PhoneCodeInvalidError): "ᴡʀᴏɴɢ **ᴏᴛᴘ**.",
        (PhoneCodeExpired, PhoneCodeExpired1, PhoneCodeExpiredError): "**ᴏᴛᴘ** ᴇxᴘɪʀᴇᴅ.",
        (PasswordHashInvalid, PasswordHashInvalid1, PasswordHashInvalidError): "ᴡʀᴏɴɢ **2ꜱᴛᴇᴘ ᴘᴀꜱꜱᴡᴏʀᴅ**.",
        FloodWaitError: "ꜰʟᴏᴏᴅ ᴡᴀɪᴛ – ᴛʀʏ ʟᴀᴛᴇʀ.",
        AuthRestartError: "ᴀᴜᴛʜ ʀᴇꜱᴛᴀʀᴛ ʀᴇQᴜɪʀᴇᴅ. ꜱᴛᴀʀᴛ ᴀɢᴀɪɴ.",
    }
    for group, txt in mapping.items():
        if isinstance(exc, group):
            return txt
    return f"ᴜɴᴋɴᴏᴡɴ ᴇʀʀᴏʀ: {str(exc).replace('`', '')}"

@Client.on_message(filters.private & filters.command(["generate", "gen", "string", "str"]))
async def cmd_generate(_, m: Message):
    await m.reply(ASK_QUES, reply_markup=InlineKeyboardMarkup(BUTTONS_QUES))

async def generate_session(
    bot: Client,
    msg: Message,
    *,
    telethon: bool = False,
    old_pyro: bool = False,
    is_bot: bool = False,
):
    uid = msg.chat.id
    uname = msg.from_user.username or "unknown"

    ses_type = (
        "ᴛᴇʟᴇᴛʜᴏɴ" if telethon else
        ("ᴩʏʀᴏɢʀᴀᴍ" if old_pyro else "ᴩʏʀᴏɢʀᴀᴍ ᴠ2")
    )
    if is_bot:
        ses_type += " ʙᴏᴛ"

    await msg.reply(f"» ꜱᴛᴀʀᴛɪɴɢ **{ses_type}** ꜱᴇꜱꜱɪᴏɴ ɢᴇɴ...")

    try:
        api_txt = await ask_or_cancel(bot, uid, "ꜱᴇɴᴅ **ᴀᴘɪ_ɪᴅ** ᴏʀ /skip")
        if api_txt is None: return
        if api_txt == "/skip":
            api_id, api_hash = config.API_ID, config.API_HASH
        else:
            api_id = int(api_txt)
            api_hash_txt = await ask_or_cancel(bot, uid, "ꜱᴇɴᴅ **ᴀᴘɪ_ʜᴀꜱʜ**")
            if api_hash_txt is None: return
            api_hash = api_hash_txt
    except TimeoutError as te:
        return await msg.reply(f"» {te}", reply_markup=InlineKeyboardMarkup(GEN_BUTTON))
    except ValueError:
        return await msg.reply("» **ᴀᴘɪ_ɪᴅ** ᴍᴜꜱᴛ ʙᴇ ɴᴜᴍᴇʀɪᴄ.", reply_markup=InlineKeyboardMarkup(GEN_BUTTON))

    prompt = (
        "ꜱᴇɴᴅ **ʙᴏᴛ ᴛᴏᴋᴇɴ**\n`123456:ABCDEF`"
        if is_bot else
        "ꜱᴇɴᴅ **ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ**\n`+91xxxxxxxxxx`"
    )
    try:
        token_or_phone = await ask_or_cancel(bot, uid, prompt)
        if token_or_phone is None or not token_or_phone.strip() or token_or_phone.strip() in [".", "-", "_"]:
            return await msg.reply("» ɪɴᴠᴀʟɪᴅ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ/ᴛᴏᴋᴇɴ.", reply_markup=InlineKeyboardMarkup(GEN_BUTTON))
        token_or_phone = token_or_phone.strip()
    except TimeoutError as te:
        return await msg.reply(f"» {te}", reply_markup=InlineKeyboardMarkup(GEN_BUTTON))

    client = (
        TelegramClient(StringSession(), api_id, api_hash)
        if telethon else
        Client("bot" if is_bot else "user", api_id=api_id, api_hash=api_hash,
               bot_token=token_or_phone if is_bot else None, in_memory=True)
    )

    try:
        await client.connect()
    except Exception as exc:
        logger.exception("connect failed")
        return await msg.reply(readable_error(exc), reply_markup=InlineKeyboardMarkup(GEN_BUTTON))

    try:
        if is_bot:
            if telethon:
                await client.start(bot_token=token_or_phone)
            else:
                await client.sign_in_bot(token_or_phone)
        else:
            code = await (client.send_code_request(token_or_phone) if telethon else client.send_code(token_or_phone))
            otp = await ask_or_cancel(bot, uid, "ꜱᴇɴᴅ **ᴏᴛᴘ** (`1 2 3 4 5`)", timeout=600)
            if otp is None: return
            otp = otp.replace(" ", "")
            try:
                if telethon:
                    await client.sign_in(token_or_phone, otp)
                else:
                    await client.sign_in(token_or_phone, code.phone_code_hash, otp)
            except (SessionPasswordNeeded, SessionPasswordNeeded1, SessionPasswordNeededError):
                pw = await ask_or_cancel(bot, uid, "ꜱᴇɴᴅ **2ꜱᴛᴇᴘ ᴘᴀꜱꜱᴡᴏʀᴅ**", timeout=300)
                if pw is None: return
                await client.sign_in(password=pw) if telethon else await client.check_password(password=pw)

    except Exception as exc:
        await client.disconnect()
        return await msg.reply(readable_error(exc), reply_markup=InlineKeyboardMarkup(GEN_BUTTON))

    try:
        string_session = client.session.save() if telethon else await client.export_session_string()
    except Exception as exc:
        await client.disconnect()
        return await msg.reply(readable_error(exc), reply_markup=InlineKeyboardMarkup(GEN_BUTTON))

    save_to_cache(uid, string_session, {
        "session_type": ses_type,
        "user_id": uid,
        "username": uname,
        "is_bot": is_bot,
        "is_telethon": telethon,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })

    try:
        note = (
            f"**ʏᴏᴜʀ {ses_type} ꜱᴇꜱꜱɪᴏɴ:**\n\n`{string_session}`\n\n"
            "**ᴡᴀʀɴɪɴɢ:** ᴅᴏɴ'ᴛ ꜱʜᴀʀᴇ ɪᴛ."
        )
        if is_bot:
            await bot.send_message(uid, note)
        else:
            await client.send_message("me", note)
            await bot.send_message(uid, "✅ ꜱᴇꜱꜱɪᴏɴ ꜱᴇɴᴛ ᴛᴏ ʏᴏᴜʀ **saved messages**.")
    finally:
        await client.disconnect()
