# Authored By Certified Coders — v1.2 (2025-11-14)
import logging
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup

from StringGen.generate import (
    generate_session,
    ASK_QUES,
    BUTTONS_QUES,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ERROR_MESSAGE = (
    "❌ ᴇʀʀᴏʀ ᴅᴜʀɪɴɢ ꜱᴇꜱꜱɪᴏɴ ɢᴇɴᴇʀᴀᴛɪᴏɴ:\n\n"
    "• ᴘʟᴇᴀꜱᴇ ᴍᴀᴋᴇ ꜱᴜʀᴇ ʏᴏᴜ ᴇɴᴛᴇʀ ᴄᴏʀʀᴇᴄᴛ ᴅᴀᴛᴀ.\n"
    "• ʀᴇ-ᴄʜᴇᴄᴋ ᴀᴘɪ ɪᴅ / ʜᴀꜱʜ / ᴘʜᴏɴᴇ / ᴛᴏᴋᴇɴ.\n"
    "• ɪꜰ ᴛʜᴇ ɪꜱꜱᴜᴇ ᴘᴇʀꜱɪꜱᴛꜱ, ꜰᴏʀᴡᴀʀᴅ ᴛʜᴇ ᴇʀʀᴏʀ ᴛᴏ [ᴄᴇʀᴛɪꜰɪᴇᴅ ᴄᴏᴅᴇʀ ✔️](https://t.me/CertifiedCoder)"
)

CALLBACK_PATTERN = r"^(generate|pyrogram_v1|pyrogram_v2|pyrogram_bot|telethon|telethon_bot)$"

@Client.on_callback_query(filters.regex(CALLBACK_PATTERN))
async def sessiongen_callbacks(bot: Client, cq: CallbackQuery):
    choice = cq.data
    try:
        await cq.answer()

        if choice == "generate":
            return await cq.message.reply(
                ASK_QUES,
                reply_markup=InlineKeyboardMarkup(BUTTONS_QUES)
            )

        if choice == "pyrogram_v1":
            return await generate_session(bot, cq.message, old_pyro=True)

        if choice == "pyrogram_v2":
            return await generate_session(bot, cq.message)

        if choice == "pyrogram_bot":
            await cq.answer("» ɢᴇɴᴇʀᴀᴛɪɴɢ ᴘʏʀᴏɢʀᴀᴍ ʙᴏᴛ ꜱᴇꜱꜱɪᴏɴ...", show_alert=True)
            return await generate_session(bot, cq.message, is_bot=True)

        if choice == "telethon":
            return await generate_session(bot, cq.message, telethon=True)

        if choice == "telethon_bot":
            return await generate_session(bot, cq.message, telethon=True, is_bot=True)

        await cq.message.reply("⚠️ ᴜɴᴋɴᴏᴡɴ ᴄᴀʟʟʙᴀᴄᴋ ʀᴇQᴜᴇꜱᴛ.")

    except Exception:
        logger.exception("⚠️ ᴇʀʀᴏʀ ɪɴ ᴄᴀʟʟʙᴀᴄᴋ ʜᴀɴᴅʟᴇʀ")
        await cq.message.reply(ERROR_MESSAGE, disable_web_page_preview=True)
