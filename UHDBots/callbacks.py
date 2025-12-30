import traceback
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup
from UHDBots.generate import generate_session, ask_ques, buttons_ques


@Client.on_callback_query(
    filters.regex(r"^(generate|pyrogram|pyrogram_bot|telethon_bot|telethon)$")
)
async def callbacks(bot: Client, cb: CallbackQuery):
    query = cb.matches[0].group(1)

    # Always answer callback immediately
    try:
        await cb.answer()
    except:
        pass

    try:
        if query == "generate":
            # Edit message instead of spamming replies
            await cb.message.edit_text(
                ask_ques,
                reply_markup=InlineKeyboardMarkup(buttons_ques)
            )

        elif query == "pyrogram":
            await generate_session(bot, cb.message)

        elif query == "pyrogram_bot":
            await cb.answer(
                "» Session will be generated using PYROGRAM v2.",
                show_alert=True
            )
            await generate_session(bot, cb.message, is_bot=True)

        elif query == "telethon":
            await generate_session(bot, cb.message, telethon=True)

        elif query == "telethon_bot":
            await generate_session(
                bot,
                cb.message,
                telethon=True,
                is_bot=True
            )

    except Exception:
        # Log full traceback to console only
        print(traceback.format_exc())

        # User-friendly error message
        await cb.message.reply(
            "❌ **An error occurred while generating your session.**\n"
            "Please try again or restart the process."
        )
