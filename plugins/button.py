# plugins/button.py
import asyncio
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputTextMessageContent, InlineQueryResultArticle
from pykeyboard import InlineKeyboard
from gc import get_objects
from config import owner_id  # Impor config jika diperlukan untuk ID pemilik

# Fungsi untuk membuat tombol kustom
async def create_button(m):
    buttons = InlineKeyboard(row_width=1)
    keyboard = []
    msg = []
    if "~" not in m.text.split(None, 1)[1]:
        for item in m.text.split(None, 1)[1].split():
            item_parts = item.split("|", 1)
            keyboard.append(
                InlineKeyboardButton(item_parts[0].replace("_", " "), url=item_parts[1])
            )
            msg.append(item_parts[0])
        buttons.add(*keyboard)
        text = m.reply_to_message.text if m.reply_to_message else " ".join(msg)
    else:
        for item in m.text.split("~", 1)[1].split():
            item_parts = item.split("|", 1)
            keyboard.append(
                InlineKeyboardButton(item_parts[0].replace("_", " "), url=item_parts[1])
            )
        buttons.add(*keyboard)
        text = m.text.split("~", 1)[0].split(None, 1)[1]
    return buttons, text

# Handler untuk perintah /button
@Client.on_message(filters.command("button") & filters.me)
async def cmd_button(client, message):
    if len(message.command) < 2:
        return await message.reply("Format salah! Gunakan: teks ~ button_name|link_url")
    
    # Cek format
    if "~" not in message.text:
        return await message.reply("Format salah! Gunakan: teks ~ button_name|link_url")

    try:
        buttons, text = await create_button(message)
        await message.reply(text, reply_markup=buttons)
    except Exception as e:
        await message.reply(f"Terjadi kesalahan: {e}")

# Handler untuk inline query tombol
@Client.on_inline_query(filters.regex("^get_button"))
async def inline_button(client, inline_query):
    get_id = int(inline_query.query.split(None, 1)[1])
    m = [obj for obj in get_objects() if id(obj) == get_id][0]
    buttons, text = await create_button(m)
    await client.answer_inline_query(
        inline_query.id,
        cache_time=0,
        results=[
            InlineQueryResultArticle(
                title="Get Button!",
                reply_markup=buttons,
                input_message_content=InputTextMessageContent(text),
            )
        ],
    )
