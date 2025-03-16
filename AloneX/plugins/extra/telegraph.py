import os
import requests
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from AloneX import app

def upload_file(file_path):
    url = "https://catbox.moe/user/api.php"
    data = {"reqtype": "fileupload", "json": "true"}
    with open(file_path, "rb") as file:
        response = requests.post(url, data=data, files={"fileToUpload": file})
    if response.status_code == 200:
        return True, response.text.strip()
    else:
        return False, f"Error: {response.status_code} - {response.text}"

@app.on_message(filters.command(["tgm", "tm", "telegraph", "tl"]))
async def get_link_group(client, message):
    if not message.reply_to_message:
        return await message.reply_text(
            "⚠️ Please reply to a media file to upload."
        )

    media = message.reply_to_message
    file_size = 0

    if media.photo:
        file_size = media.photo.file_size
    elif media.video:
        file_size = media.video.file_size
    elif media.document:
        file_size = media.document.file_size

    if file_size == 0:
        return await message.reply_text("⚠️ This message doesn't contain any downloadable media.")

    if file_size > 200 * 1024 * 1024:
        return await message.reply_text("⚠️ Please provide a media file under 200MB.")

    text = await message.reply("🔄 𝐏ʀᴏᴄᴇssɪɴɢ 𝐘ᴏᴜʀ 𝐅ɪʟᴇ...")

    async def progress(current, total):
        try:
            await text.edit_text(f"Downloading... {current * 100 / total:.1f}%")
        except Exception:
            pass

    try:
        local_path = await media.download(progress=progress)

        if not os.path.exists(local_path):
            return await text.edit_text("❌ Failed to download the media.")

        await text.edit_text("𝐔ᴘʟᴏᴀᴅᴇᴅ 𝐓ᴏ 𝐘ᴏᴜʀ 𝐓ᴇʟᴇɢʀᴀᴘʜ...")

        success, result = upload_file(local_path)

        if success:
            await message.reply_photo(
                local_path,
                caption=f"✨ {message.from_user.mention(style='md')}, 𝐓ʜɪs 𝐈s 𝐘ᴏᴜʀ 𝐔ᴘʟᴏᴀᴅᴇᴅ 𝐌ᴇᴅɪᴀ!",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("𝐓ᴇʟᴇɢʀᴀᴘʜ 𝐋ɪɴᴋ", url=result)]]
                ),
            )
        else:
            await text.edit_text(f"❌ 𝐔ᴘʟᴏᴀᴅ 𝐅ᴀɪʟᴇᴅ!\nError: {result}")

    except Exception as e:
        await text.edit_text(f"❌ An error occurred:\n{e}")

    finally:
        try:
            if os.path.exists(local_path):
                os.remove(local_path)
        except Exception:
            pass
