from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from AloneX import app
from config import BOT_USERNAME

start_txt = """
**
┌┬─────────────────⦿
│├─────────────────╮
│├ 𝗧ɢ 𝗡ᴀᴍᴇ - [💗 ❥ＭＹ ＢＡＢＹ❥ 💗](https://t.me/D_I_Y_O_R_r_N_e_x_t_y)
│├ 𝗙ᴜʟʟ 𝗜ɴғᴏ - [𝐂ʟɪᴄᴋ 𝐇ᴇʀᴇ](https://t.me/+m6vFF4Vy9hM4YjY1)
│├─────────────────╯
├┼─────────────────⦿
│├─────────────────╮
│├ 𝗢ᴡɴᴇʀ│ [👑 『𝘽𝘼𝘽𝙔』 👑](https://t.me/D_I_Y_O_R_r_N_e_x_t_y)
│├─────────────────╯
└┴─────────────────⦿
**
"""

@app.on_message(filters.command("repo"))
async def repo_command(client, message):
    buttons = [
        [ 
            InlineKeyboardButton("💥 『ＦＩＧＨＴＥＲ  ＧＲＯＵＰ』 💥", url="https://t.me/+Lldixy-QOnMwOTc1")
        ],
        [
            InlineKeyboardButton("❤️ 『𝘖𝘍𝘍𝘐𝘊𝘐𝘈𝘓 𝘎𝘙𝘖𝘜𝘗』 ❤️", url="https://t.me/+m6vFF4Vy9hM4YjY1"),
            InlineKeyboardButton("👑 『𝘽𝘼𝘽𝙔』 👑", url="https://t.me/RAJARAJ909"),
        ],
        [
            InlineKeyboardButton("💗 ❥ＭＹ ＢＡＢＹ❥ 💗", url="https://t.me/D_I_Y_O_R_r_N_e_x_t_y"),
        ],
        [
            InlineKeyboardButton("OFFICIAL BOT", url="https://t.me/bebiejaann_bot"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    try:
        await message.reply_photo(
            photo="https://files.catbox.moe/y9d9k9.jpg",
            caption=start_txt,
            reply_markup=reply_markup
        )
    except Exception as e:
        await message.reply_text(
            text=start_txt,
            reply_markup=reply_markup
        )
        print(f"Failed to send photo: {e}")

# Add help command
@app.on_message(filters.command("help"))
async def help_command(client, message):
    help_text = """
**Available Commands:**
/repo - Get repository information
/help - Show this help message
"""
    await message.reply_text(help_text)