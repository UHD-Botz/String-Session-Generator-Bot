from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from pyrogram.errors import UserNotParticipant, ChatAdminRequired
from config import OWNER_ID, F_SUB
from UHDBots.db import db


def welcome_text(me, user):
    return (
        f"<b>𝐇𝐞𝐲 {user.mention}🍷,\n\n"
        f"ɪ ᴀᴍ {me},\n"
        f"ᴛʀᴜsᴛᴇᴅ 𝗦𝗧𝗥𝗜𝗡𝗚 𝗚𝗘𝗡𝗘𝗥𝗔𝗧𝗢𝗥 ʙᴏᴛ.\n"
        f"ғᴜʟʟʏ sᴀғᴇ & sᴇᴄᴜʀᴇ.\n\n"
        f"Made With ❤️ By : <a href='https://t.me/UHDBots'>UHD Bots</a></b>"
    )


def welcome_buttons():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("⚡ Generate String Session ⚡", callback_data="generate")],
            [
                InlineKeyboardButton("❣️ Support Group ❣️", url="https://t.me/UHDBots_Support"),
                InlineKeyboardButton("🥀 Update Channel 🥀", url="https://t.me/UHDBots")
            ]
        ]
    )


@Client.on_message(filters.private & filters.command("start"))
async def start(bot: Client, msg: Message):
    user_id = msg.from_user.id

    if not await db.is_user_exist(user_id):
        await db.add_user(user_id, msg.from_user.first_name)

    # Force Subscribe Check
    if F_SUB:
        try:
            await bot.get_chat_member(int(F_SUB), user_id)
        except UserNotParticipant:
            try:
                invite = await bot.create_chat_invite_link(int(F_SUB))
            except ChatAdminRequired:
                await msg.reply_text("❌ **Make sure I am admin in the update channel.**")
                return

            buttons = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("🍿 Join Update Channel 🍿", url=invite.invite_link)],
                    [InlineKeyboardButton("🍀 Check Again 🍀", callback_data="chk")]
                ]
            )

            await msg.reply_text(
                "**⚠️ Access Denied!\n\n"
                "Please join my update channel to use me.\n"
                "After joining, click `Check Again`.**",
                reply_markup=buttons
            )
            return

    me = (await bot.get_me()).mention
    await msg.reply_text(
        welcome_text(me, msg.from_user),
        reply_markup=welcome_buttons(),
        disable_web_page_preview=True
    )


@Client.on_callback_query(filters.regex("^chk$"))
async def chk(bot: Client, cb: CallbackQuery):
    user_id = cb.from_user.id

    try:
        await bot.get_chat_member(int(F_SUB), user_id)
    except UserNotParticipant:
        await cb.answer(
            "🙅‍♂️ You have not joined the channel yet.",
            show_alert=True
        )
        return

    me = (await bot.get_me()).mention
    await cb.message.edit_text(
        welcome_text(me, cb.from_user),
        reply_markup=welcome_buttons(),
        disable_web_page_preview=True
    )
    await cb.answer()
