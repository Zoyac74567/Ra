import config
import asyncio
from time import time, strftime, gmtime
from pyrogram import filters, __version__ as pver
from pyrogram.types import (
    InputMediaVideo, 
    InputMediaPhoto,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message
)
from pyrogram.enums import ChatType
from pyrogram.errors import (
    MessageNotModified,
    FloodWait,
    PeerIdInvalid,
    UserNotParticipant
)

from AloneX import app, LOGGER
from AloneX.utils.database import (
    add_nonadmin_chat,
    get_authuser,
    get_authuser_names,
    get_playmode,
    get_playtype,
    get_upvote_count,
    is_nonadmin_chat,
    is_skipmode,
    remove_nonadmin_chat,
    set_playmode,
    set_playtype,
    set_upvotes,
    skip_off,
    skip_on,
)
from AloneX.utils.decorators.admins import ActualAdminCB
from AloneX.utils.decorators.language import language, languageCB
from AloneX.utils.inline.settings import (
    auth_users_markup,
    playmode_users_markup,
    setting_markup,
    vote_mode_markup,
)
from AloneX.utils.inline.start import private_panel
from config import BANNED_USERS, OWNER_ID

# Constants
SETTINGS_GROUP_COMMANDS = ["settings", "setting"]
START_MEDIA = InputMediaPhoto(media=config.START_IMG_URL)
SOURCE_MEDIA = InputMediaVideo(
    "https://files.catbox.moe/ehi6fc.mp4",
    has_spoiler=True,
    caption="Music Repo Now Public Type - /repo"
)

class SettingsHandler:
    def __init__(self):
        self.start_time = time()
    
    async def error_handler(self, func, *args, **kwargs):
        """Handle common errors gracefully"""
        try:
            return await func(*args, **kwargs)
        except MessageNotModified:
            pass
        except FloodWait as e:
            LOGGER.warning(f"FloodWait: Sleeping for {e.value} seconds")
            await asyncio.sleep(e.value)
            return await func(*args, **kwargs)
        except Exception as e:
            LOGGER.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
            if args and isinstance(args[0], (CallbackQuery, Message)):
                await args[0].message.reply_text("❌ An error occurred. Please try again later.")
            return None
    
    @app.on_message(
        filters.command(SETTINGS_GROUP_COMMANDS) & 
        filters.group & 
        ~BANNED_USERS
    )
    @language
    async def settings_command(self, client, message: Message, _):
        """Handle /settings command in groups"""
        buttons = setting_markup(_)
        await self.error_handler(
            message.reply_text,
            _["setting_1"].format(
                app.mention, 
                message.chat.id, 
                message.chat.title
            ),
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    @app.on_callback_query(filters.regex("settings_helper") & ~BANNED_USERS)
    @languageCB
    async def settings_callback(self, client, cb: CallbackQuery, _):
        """Main settings callback handler"""
        await self.error_handler(
            cb.answer, 
            _["set_cb_5"], 
            show_alert=True
        )
        
        buttons = setting_markup(_)
        await self.error_handler(
            cb.edit_message_text,
            _["setting_1"].format(
                app.mention,
                cb.message.chat.id,
                cb.message.chat.title,
            ),
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    @app.on_callback_query(filters.regex("settingsback_helper") & ~BANNED_USERS)
    @languageCB
    async def settings_back(self, client, cb: CallbackQuery, _):
        """Back button handler for settings"""
        await self.error_handler(cb.answer)
        
        if cb.message.chat.type == ChatType.PRIVATE:
            try:
                await app.resolve_peer(OWNER_ID)
                buttons = private_panel(_)
                await self.error_handler(
                    cb.edit_message_media,
                    START_MEDIA,
                    caption=_["start_2"].format(
                        cb.from_user.mention, 
                        app.mention
                    ),
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
            except PeerIdInvalid:
                await cb.message.reply_text("❌ Could not resolve owner ID")
        else:
            buttons = setting_markup(_)
            await self.error_handler(
                cb.edit_message_reply_markup,
                reply_markup=InlineKeyboardMarkup(buttons)
            )

    @app.on_callback_query(filters.regex("gib_source"))
    async def source_callback(self, _, cb: CallbackQuery):
        """Source code information handler"""
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("• ʙᴀᴄᴋ •", "settingsback_helper"),
                InlineKeyboardButton("• ᴄʟᴏsᴇ •", "close")
            ]
        ])
        
        await self.error_handler(
            cb.edit_message_media,
            media=SOURCE_MEDIA,
            reply_markup=buttons
        )

    @app.on_callback_query(filters.regex("^bot_info_data$"))
    async def bot_info_callback(self, client, cb: CallbackQuery):
        """Bot technical information handler"""
        start_time = time()
        try:
            test_msg = await client.send_message(cb.message.chat.id, "🏓 Pinging...")
            delta_ping = (time() - start_time) * 1000
            
            info_text = f"""
⚡ Bot Information:

• 🏓 Ping: {delta_ping:.3f} ms
• 🐍 Python Version: 3.10.4
• 🔥 Pyrogram Version: {pver}
• 🚀 Uptime: {strftime('%Hh %Mm %Ss', gmtime(time() - self.start_time))}
• 💾 Database: {'Connected' if app.db else 'Disconnected'}
"""
            await test_msg.delete()
            await cb.answer(info_text, show_alert=True)
        except Exception as e:
            LOGGER.error(f"Error in bot_info: {str(e)}")
            await cb.answer("❌ Failed to get bot info", show_alert=True)

    @app.on_callback_query(filters.regex("alone_op") & ~BANNED_USERS)
    @languageCB
    async def support_menu(self, client, cb: CallbackQuery, _):
        """Support links menu handler"""
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ", url=config.SUPPORT_CHAT),
                InlineKeyboardButton("ᴄʜᴀɴɴᴇʟ", url=config.SUPPORT_CHANNEL)
            ],
            [
                InlineKeyboardButton("ʙᴀᴄᴋ", "settingsback_helper")
            ]
        ])
        
        await self.error_handler(
            cb.edit_message_text,
            text="🔗 Important Links:",
            reply_markup=buttons
        )

    @app.on_callback_query(
        filters.regex(
            r"^(SEARCHANSWER|PLAYMODEANSWER|PLAYTYPEANSWER|AUTHANSWER|ANSWERVOMODE|VOTEANSWER|PM|AU|VM)$"
        ) & ~BANNED_USERS
    )
    @languageCB
    async def settings_info_callback(self, client, cb: CallbackQuery, _):
        """Settings information callback handler"""
        command = cb.matches[0].group(1)
        
        info_messages = {
            "SEARCHANSWER": _["setting_2"],
            "PLAYMODEANSWER": _["setting_5"],
            "PLAYTYPEANSWER": _["setting_6"],
            "AUTHANSWER": _["setting_3"],
            "VOTEANSWER": _["setting_8"],
        }
        
        if command in info_messages:
            await self.error_handler(
                cb.answer,
                info_messages[command],
                show_alert=True
            )
            return
        
        if command == "ANSWERVOMODE":
            current = await get_upvote_count(cb.message.chat.id)
            await self.error_handler(
                cb.answer,
                _["setting_9"].format(current),
                show_alert=True
            )
            return
        
        # Mode change handlers
        if command == "PM":
            await self.error_handler(
                cb.answer,
                _["set_cb_2"],
                show_alert=True
            )
            
            playmode = await get_playmode(cb.message.chat.id)
            is_non_admin = await is_nonadmin_chat(cb.message.chat.id)
            playty = await get_playtype(cb.message.chat.id)
            
            buttons = playmode_users_markup(
                _,
                Direct=(playmode == "Direct"),
                Group=not is_non_admin,
                Playtype=(playty != "Everyone")
            )
        
        elif command == "AU":
            await self.error_handler(
                cb.answer,
                _["set_cb_1"],
                show_alert=True
            )
            is_non_admin = await is_nonadmin_chat(cb.message.chat.id)
            buttons = auth_users_markup(_, not is_non_admin)
        
        elif command == "VM":
            mode = await is_skipmode(cb.message.chat.id)
            current = await get_upvote_count(cb.message.chat.id)
            buttons = vote_mode_markup(_, current, mode)
        
        await self.error_handler(
            cb.edit_message_reply_markup,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    @app.on_callback_query(filters.regex("FERRARIUDTI") & ~BANNED_USERS)
    @ActualAdminCB
    @languageCB
    async def vote_settings_handler(self, client, cb: CallbackQuery, _):
        """Vote mode settings handler"""
        callback_data = cb.data.strip()
        mode = callback_data.split(None, 1)[1]
        
        if not await is_skipmode(cb.message.chat.id):
            return await cb.answer(_["setting_10"], show_alert=True)
        
        current = await get_upvote_count(cb.message.chat.id)
        
        if mode == "M":
            final = max(2, current - 2)
            if final == 0:
                return await cb.answer(_["setting_11"], show_alert=True)
        else:
            final = min(15, current + 2)
            if final == 17:
                return await cb.answer(_["setting_12"], show_alert=True)
        
        await set_upvotes(cb.message.chat.id, final)
        buttons = vote_mode_markup(_, final, True)
        
        await self.error_handler(
            cb.edit_message_reply_markup,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    @app.on_callback_query(
        filters.regex(pattern=r"^(MODECHANGE|CHANNELMODECHANGE|PLAYTYPECHANGE)$") & 
        ~BANNED_USERS
    )
    @ActualAdminCB
    @languageCB
    async def playmode_settings_handler(self, client, cb: CallbackQuery, _):
        """Play mode settings handler"""
        command = cb.matches[0].group(1)
        
        if command == "CHANNELMODECHANGE":
            is_non_admin = await is_nonadmin_chat(cb.message.chat.id)
            if not is_non_admin:
                await add_nonadmin_chat(cb.message.chat.id)
                Group = None
            else:
                await remove_nonadmin_chat(cb.message.chat.id)
                Group = True
            
            playmode = await get_playmode(cb.message.chat.id)
            playty = await get_playtype(cb.message.chat.id)
            
            buttons = playmode_users_markup(
                _,
                Direct=(playmode == "Direct"),
                Group=Group,
                Playtype=(playty != "Everyone")
            )
        
        elif command == "MODECHANGE":
            await self.error_handler(
                cb.answer,
                _["set_cb_3"],
                show_alert=True
            )
            
            playmode = await get_playmode(cb.message.chat.id)
            if playmode == "Direct":
                await set_playmode(cb.message.chat.id, "Inline")
                Direct = None
            else:
                await set_playmode(cb.message.chat.id, "Direct")
                Direct = True
            
            is_non_admin = await is_nonadmin_chat(cb.message.chat.id)
            playty = await get_playtype(cb.message.chat.id)
            
            buttons = playmode_users_markup(
                _,
                Direct=Direct,
                Group=not is_non_admin,
                Playtype=(playty != "Everyone")
            )
        
        elif command == "PLAYTYPECHANGE":
            await self.error_handler(
                cb.answer,
                _["set_cb_3"],
                show_alert=True
            )
            
            playty = await get_playtype(cb.message.chat.id)
            if playty == "Everyone":
                await set_playtype(cb.message.chat.id, "Admin")
                Playtype = False
            else:
                await set_playtype(cb.message.chat.id, "Everyone")
                Playtype = True
            
            playmode = await get_playmode(cb.message.chat.id)
            is_non_admin = await is_nonadmin_chat(cb.message.chat.id)
            
            buttons = playmode_users_markup(
                _,
                Direct=(playmode == "Direct"),
                Group=not is_non_admin,
                Playtype=Playtype
            )
        
        await self.error_handler(
            cb.edit_message_reply_markup,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    @app.on_callback_query(filters.regex(pattern=r"^(AUTH|AUTHLIST)$") & ~BANNED_USERS)
    @ActualAdminCB
    @languageCB
    async def auth_settings_handler(self, client, cb: CallbackQuery, _):
        """Authorization settings handler"""
        command = cb.matches[0].group(1)
        
        if command == "AUTHLIST":
            _authusers = await get_authuser_names(cb.message.chat.id)
            if not _authusers:
                return await self.error_handler(
                    cb.answer,
                    _["setting_4"],
                    show_alert=True
                )
            
            await self.error_handler(
                cb.answer,
                _["set_cb_4"],
                show_alert=True
            )
            
            j = 0
            await cb.edit_message_text(_["auth_6"])
            msg = _["auth_7"].format(cb.message.chat.title)
            
            for note in _authusers:
                _note = await get_authuser(cb.message.chat.id, note)
                user_id = _note["auth_user_id"]
                admin_id = _note["admin_id"]
                admin_name = _note["admin_name"]
                
                try:
                    user = await app.get_users(user_id)
                    user = user.first_name
                    j += 1
                except:
                    continue
                
                msg += f"{j}➤ {user}[<code>{user_id}</code>]\n"
                msg += f"   {_['auth_8']} {admin_name}[<code>{admin_id}</code>]\n\n"
            
            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(_["BACK_BUTTON"], callback_data="AU"),
                    InlineKeyboardButton(_["CLOSE_BUTTON"], callback_data="close"),
                ]
            ])
            
            await self.error_handler(
                cb.edit_message_text,
                msg,
                reply_markup=buttons
            )
            return
        
        await self.error_handler(
            cb.answer,
            _["set_cb_3"],
            show_alert=True
        )
        
        if command == "AUTH":
            is_non_admin = await is_nonadmin_chat(cb.message.chat.id)
            if not is_non_admin:
                await add_nonadmin_chat(cb.message.chat.id)
                buttons = auth_users_markup(_)
            else:
                await remove_nonadmin_chat(cb.message.chat.id)
                buttons = auth_users_markup(_, True)
            
            await self.error_handler(
                cb.edit_message_reply_markup,
                reply_markup=InlineKeyboardMarkup(buttons)
            )

    @app.on_callback_query(filters.regex("VOMODECHANGE") & ~BANNED_USERS)
    @ActualAdminCB
    @languageCB
    async def vote_mode_handler(self, client, cb: CallbackQuery, _):
        """Vote mode toggle handler"""
        await self.error_handler(
            cb.answer,
            _["set_cb_3"],
            show_alert=True
        )
        
        mod = None
        if await is_skipmode(cb.message.chat.id):
            await skip_off(cb.message.chat.id)
        else:
            mod = True
            await skip_on(cb.message.chat.id)
        
        current = await get_upvote_count(cb.message.chat.id)
        buttons = vote_mode_markup(_, current, mod)
        
        await self.error_handler(
            cb.edit_message_reply_markup,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

# Initialize the handler
settings_handler = SettingsHandler()