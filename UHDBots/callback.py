import traceback
from pyrogram import Client
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from Script import text
from config import ADMIN
from .main import generate_session, ask_ques, buttons_ques

@Client.on_callback_query()
async def callback_query_handler(client, query: CallbackQuery):
    data = query.data

    try:
        if data == "start":
            await query.message.edit_text(
                text.START.format(query.from_user.mention),
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton('ᴀʙᴏᴜᴛ', callback_data='about'),
                     InlineKeyboardButton('ʜᴇʟᴘ', callback_data='help')],
                    [InlineKeyboardButton('ɢᴇɴᴇʀᴀᴛᴇ sᴛʀɪɴɢ sᴇssɪᴏɴ', callback_data='generate')]
                ])
            )

        elif data == "help":
            await query.message.edit_text(
                text.HELP.format(query.from_user.mention),
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton('ᴜᴩᴅᴀᴛᴇꜱ', url='https://telegram.me/Techifybots'),
                     InlineKeyboardButton('ꜱᴜᴩᴩᴏʀᴛ', url='https://telegram.me/TechifySupport')],
                    [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="start"),
                     InlineKeyboardButton("ᴄʟᴏꜱᴇ", callback_data="close")]
                ])
            )

        elif data == "about":
            await query.message.edit_text(
                text.ABOUT,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton('💥 ʀᴇᴘᴏ', url='https://github.com/TechifyBots/String-Session-Bot'),
                     InlineKeyboardButton('👨‍💻 ᴏᴡɴᴇʀ', user_id=int(ADMIN))],
                    [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="start"),
                     InlineKeyboardButton("ᴄʟᴏꜱᴇ", callback_data="close")]
                ])
            )

        elif data == "close":
            await query.message.delete()
            await query.answer()

        elif data == "generate":
            await query.answer()
            await query.message.reply(ask_ques, reply_markup=InlineKeyboardMarkup(buttons_ques))

        elif data in ["pyrogram", "pyrogram_bot", "telethon", "telethon_bot"]:
            await query.answer()
            if data == "pyrogram":
                await generate_session(client, query.message)
            elif data == "pyrogram_bot":
                await query.answer("» ᴛʜᴇ sᴇssɪᴏɴ ɢᴇɴᴇʀᴀᴛᴇᴅ ᴡɪʟʟ ʙᴇ ᴏғ ᴩʏʀᴏɢʀᴀᴍ ᴠ2.", show_alert=True)
                await generate_session(client, query.message, is_bot=True)
            elif data == "telethon":
                await generate_session(client, query.message, telethon=True)
            elif data == "telethon_bot":
                await generate_session(client, query.message, telethon=True, is_bot=True)

    except Exception as e:
        print(traceback.format_exc())
        await query.message.reply(f"**Error -** `{e}`")
