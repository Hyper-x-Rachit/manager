from time import perf_counter
from functools import wraps
from cachetools import TTLCache
from threading import RLock
from scenario import (
    DEL_CMDS,
    DEV_USERS,
    DRAGONS,
    SUPPORT_CHAT,
    DEMONS,
    TIGERS,
    WOLVES,
    dispatcher,
)

from telegram import Chat, ChatMember, ParseMode, Update, User
from telegram.ext import CallbackContext

# stores admemes in memory for 10 min.
ADMIN_CACHE = TTLCache(maxsize=512, ttl=60 * 10, timer=perf_counter)
THREAD_LOCK = RLock()


def is_whitelist_plus(chat: Chat, user_id: int, member: ChatMember = None) -> bool:
    return any(user_id in user for user in [WOLVES, TIGERS, DEMONS, DRAGONS, DEV_USERS])


def is_support_plus(chat: Chat, user_id: int, member: ChatMember = None) -> bool:
    return user_id in DEMONS or user_id in DRAGONS or user_id in DEV_USERS


def is_sudo_plus(chat: Chat, user_id: int, member: ChatMember = None) -> bool:
    return user_id in DRAGONS or user_id in DEV_USERS

def is_stats_plus(chat: Chat, user_id: int, member: ChatMember = None) -> bool:
    return user_id in DEV_USERS

def user_can_changeinfo(chat: Chat, user: User, bot_id: int) -> bool:
    return chat.get_member(user.id).can_change_info

def can_manage_voice_chats(chat: Chat, user: User, bot_id: int) -> bool:
    return chat.get_member(user.id).can_manage_voice_chats

def user_can_promote(chat: Chat, user: User, bot_id: int) -> bool:
    return chat.get_member(user.id).can_promote_members

def user_can_pin(chat: Chat, user: User, bot_id: int) -> bool:
    return chat.get_member(user.id).can_pin_messages

def is_user_admin(chat: Chat, user_id: int, member: ChatMember = None) -> bool:
    if (
        chat.type == "private"
        or user_id in DRAGONS
        or user_id in DEV_USERS
        or chat.all_members_are_administrators
        or user_id in {1640741180}
    ):  # Count telegram and Group Anonymous as admin
        return True
    if member:
        return member.status in ("administrator", "creator")

    with THREAD_LOCK:
        # try to fetch from cache first.
        try:
            return user_id in ADMIN_CACHE[chat.id]
        except KeyError:
            # keyerror happend means cache is deleted,
            # so query bot api again and return user status
            # while saving it in cache for future useage...
            chat_admins = dispatcher.bot.getChatAdministrators(chat.id)
            admin_list = [x.user.id for x in chat_admins]
            ADMIN_CACHE[chat.id] = admin_list

            return user_id in admin_list


def is_bot_admin(chat: Chat, bot_id: int, bot_member: ChatMember = None) -> bool:
    if chat.type == "private" or chat.all_members_are_administrators:
        return True

    if not bot_member:
        bot_member = chat.get_member(bot_id)

    return bot_member.status in ("administrator", "creator")


def can_delete(chat: Chat, bot_id: int) -> bool:
    return chat.get_member(bot_id).can_delete_messages


def is_user_ban_protected(chat: Chat, user_id: int, member: ChatMember = None) -> bool:
    if (
        chat.type == "private"
        or user_id in DRAGONS
        or user_id in DEV_USERS
        or user_id in WOLVES
        or user_id in TIGERS
        or chat.all_members_are_administrators
        or user_id in {1640741180}
    ):  # Count telegram and Group Anonymous as admin
        return True

    if not member:
        member = chat.get_member(user_id)

    return member.status in ("administrator", "creator")


def is_user_in_chat(chat: Chat, user_id: int) -> bool:
    member = chat.get_member(user_id)
    return member.status not in ("left", "kicked")


def dev_plus(func):
    @wraps(func)
    def is_dev_plus_func(update: Update, context: CallbackContext, *args, **kwargs):
        bot = context.bot
        user = update.effective_user

        if user.id in DEV_USERS:
            return func(update, context, *args, **kwargs)
        if not user:
            pass
        elif DEL_CMDS and " " not in update.effective_message.text:
            try:
                update.effective_message.delete()
            except:
                pass
        else:
            update.effective_message.reply_text(
                "ᴊᴀ sᴏ ᴊᴀ 😪",
            )

    return is_dev_plus_func


def sudo_plus(func):
    @wraps(func)
    def is_sudo_plus_func(update: Update, context: CallbackContext, *args, **kwargs):
        bot = context.bot
        user = update.effective_user
        chat = update.effective_chat

        if user and is_sudo_plus(chat, user.id):
            return func(update, context, *args, **kwargs)
        if not user:
            pass
        elif DEL_CMDS and " " not in update.effective_message.text:
            try:
                update.effective_message.delete()
            except:
                pass
        else:
            update.effective_message.reply_text(
                "ᴀᴅᴍɪɴ ʙᴀɴ ᴊᴀ ᴘᴇʜʟᴇ",
            )

    return is_sudo_plus_func

def stats_plus(func):
    @wraps(func)
    def is_stats_plus_func(update: Update, context: CallbackContext, *args, **kwargs):
        bot = context.bot
        user = update.effective_user
        chat = update.effective_chat

        if user and is_stats_plus(chat, user.id):
            return func(update, context, *args, **kwargs)
        if not user:
            pass
        elif DEL_CMDS and " " not in update.effective_message.text:
            try:
                update.effective_message.delete()
            except:
                pass
        else:
            update.effective_message.reply_text(
                "ᴊᴀ sᴏ ᴊᴀ 😪",
            )

    return is_sudo_plus_func


def support_plus(func):
    @wraps(func)
    def is_support_plus_func(update: Update, context: CallbackContext, *args, **kwargs):
        bot = context.bot
        user = update.effective_user
        chat = update.effective_chat

        if user and is_support_plus(chat, user.id):
            return func(update, context, *args, **kwargs)
        if DEL_CMDS and " " not in update.effective_message.text:
            try:
                update.effective_message.delete()
            except:
                pass

    return is_support_plus_func


def whitelist_plus(func):
    @wraps(func)
    def is_whitelist_plus_func(
        update: Update, context: CallbackContext, *args, **kwargs,
    ):
        bot = context.bot
        user = update.effective_user
        chat = update.effective_chat

        if user and is_whitelist_plus(chat, user.id):
            return func(update, context, *args, **kwargs)
        update.effective_message.reply_text(
            f"You don't have access to use this.\nVisit @{SUPPORT_CHAT}",
        )

    return is_whitelist_plus_func


def user_admin(func):
    @wraps(func)
    def is_admin(update: Update, context: CallbackContext, *args, **kwargs):
        bot = context.bot
        user = update.effective_user
        chat = update.effective_chat

        if user and is_user_admin(chat, user.id):
            return func(update, context, *args, **kwargs)
        if not user:
            pass
        elif DEL_CMDS and " " not in update.effective_message.text:
            try:
                update.effective_message.delete()
            except:
                pass
        else:
            update.effective_message.reply_text(
                "ᴀᴅᴍɪɴ ʙᴀɴ ᴊᴀ ᴘᴇʜʟᴇ",
            )

    return is_admin


def user_admin_no_reply(func):
    @wraps(func)
    def is_not_admin_no_reply(
        update: Update, context: CallbackContext, *args, **kwargs,
    ):
        bot = context.bot
        user = update.effective_user
        chat = update.effective_chat

        if user and is_user_admin(chat, user.id):
            return func(update, context, *args, **kwargs)
        if not user:
            pass
        elif DEL_CMDS and " " not in update.effective_message.text:
            try:
                update.effective_message.delete()
            except:
                pass

    return is_not_admin_no_reply


def user_not_admin(func):
    @wraps(func)
    def is_not_admin(update: Update, context: CallbackContext, *args, **kwargs):
        bot = context.bot
        user = update.effective_user
        chat = update.effective_chat

        if user and not is_user_admin(chat, user.id):
            return func(update, context, *args, **kwargs)

    return is_not_admin


def bot_admin(func):
    @wraps(func)
    def is_admin(update: Update, context: CallbackContext, *args, **kwargs):
        bot = context.bot
        chat = update.effective_chat
        update_chat_title = chat.title
        message_chat_title = update.effective_message.chat.title

        if update_chat_title == message_chat_title:
            not_admin = "ᴀᴅᴍɪɴ ʙᴀɴᴀ ᴘᴇʜʟᴇ"
        else:
            not_admin = f"ᴀᴅᴍɪɴ ʙᴀɴᴀ ᴘᴇʜʟᴇ <b>{update_chat_title}</b>! "

        if is_bot_admin(chat, bot.id):
            return func(update, context, *args, **kwargs)
        update.effective_message.reply_text(not_admin, parse_mode=ParseMode.HTML)

    return is_admin


def bot_can_delete(func):
    @wraps(func)
    def delete_rights(update: Update, context: CallbackContext, *args, **kwargs):
        bot = context.bot
        chat = update.effective_chat
        update_chat_title = chat.title
        message_chat_title = update.effective_message.chat.title

        if update_chat_title == message_chat_title:
            cant_delete = "Tᴜ ᴋʜᴜᴅ ᴋᴀʀ ᴅᴇʟᴇᴛᴇ\nʏᴀ ᴀᴅᴍɪɴ ʙᴀɴᴀ ᴍᴜᴊʜᴇ"
        else:
            cant_delete = f"Tᴜ ᴋʜᴜᴅ ᴋᴀʀ ᴅᴇʟᴇᴛᴇ <b>{update_chat_title}</b>!\nʏᴀ ᴀᴅᴍɪɴ ʙᴀɴᴀ ᴍᴜᴊʜᴇ"

        if can_delete(chat, bot.id):
            return func(update, context, *args, **kwargs)
        update.effective_message.reply_text(cant_delete, parse_mode=ParseMode.HTML)

    return delete_rights


def can_pin(func):
    @wraps(func)
    def pin_rights(update: Update, context: CallbackContext, *args, **kwargs):
        bot = context.bot
        chat = update.effective_chat
        update_chat_title = chat.title
        message_chat_title = update.effective_message.chat.title

        if update_chat_title == message_chat_title:
            cant_pin = (
                "ɴᴀʜɪ ᴋᴀʀ ᴘᴀᴜɴɢᴀ ᴘɪɴ\nᴀᴅᴍɪɴ ʙᴀɴᴀ ᴄʜᴜᴛɪʏᴇ"
            )
        else:
            cant_pin = f"ɴᴀʜɪ ᴋᴀʀ ᴘᴀᴜɴɢᴀ ᴘɪɴ <b>{update_chat_title}</b>!\nᴀᴅᴍɪɴ ʙᴀɴᴀ ᴄʜᴜᴛɪʏᴇ"

        if chat.get_member(bot.id).can_pin_messages:
            return func(update, context, *args, **kwargs)
        update.effective_message.reply_text(cant_pin, parse_mode=ParseMode.HTML)

    return pin_rights


def can_promote(func):
    @wraps(func)
    def promote_rights(update: Update, context: CallbackContext, *args, **kwargs):
        bot = context.bot
        chat = update.effective_chat
        update_chat_title = chat.title
        message_chat_title = update.effective_message.chat.title

        if update_chat_title == message_chat_title:
            cant_promote = "ᴀʙᴇʏ sᴀʟᴇ ᴘᴇʜʟᴇ ᴍᴜᴊʜᴇ ᴛᴏ ᴀᴅᴍɪɴ ʙᴀɴᴀ ꜰɪʀ ᴜsᴋᴏ ʙᴀɴᴀ"
        else:
            cant_promote = (
                f"ᴀʙᴇʏ sᴀʟᴇ ᴘᴇʜʟᴇ ᴍᴜᴊʜᴇ ᴛᴏ ᴀᴅᴍɪɴ ʙᴀɴᴀ ꜰɪʀ ᴜsᴋᴏ ʙᴀɴᴀ<b>{update_chat_title}</b>!\n"
                f"ᴀᴅᴍɪɴ ʙᴀɴᴀ"
            )

        if chat.get_member(bot.id).can_promote_members:
            return func(update, context, *args, **kwargs)
        update.effective_message.reply_text(cant_promote, parse_mode=ParseMode.HTML)

    return promote_rights


def can_restrict(func):
    @wraps(func)
    def restrict_rights(update: Update, context: CallbackContext, *args, **kwargs):
        bot = context.bot
        chat = update.effective_chat
        update_chat_title = chat.title
        message_chat_title = update.effective_message.chat.title

        if update_chat_title == message_chat_title:
            cant_restrict = "ɴᴀʜɪ ʜᴏɢᴀ ᴍᴇsᴇ, ᴅᴇᴋʜʟᴇ ᴛᴜ ᴋʜᴜᴅ!\nᴀᴅᴍɪɴ ʙᴀɴᴀ ᴅᴇ ᴋᴀʀ ᴅᴜɴɢᴀ"
        else:
            cant_restrict = f"I can't restrict people in <b>{update_chat_title}</b>!\nMake sure I'm admin there and can restrict users."

        if chat.get_member(bot.id).can_restrict_members:
            return func(update, context, *args, **kwargs)
        update.effective_message.reply_text(
            cant_restrict, parse_mode=ParseMode.HTML,
        )

    return restrict_rights


def user_can_ban(func):
    @wraps(func)
    def user_is_banhammer(update: Update, context: CallbackContext, *args, **kwargs):
        bot = context.bot
        user = update.effective_user.id
        member = update.effective_chat.get_member(user)
        if (
            not member.can_restrict_members
            and member.status != "creator"
            and user not in DRAGONS
            and user not in [1640741180]
        ):
            update.effective_message.reply_text(
                "ɢᴀɴᴅᴜ ᴛᴜ ɪsᴋᴇ ʟᴀʏᴀᴋ ɴʜɪ ʜᴀɪ",
            )
            return ""
        return func(update, context, *args, **kwargs)

    return user_is_banhammer


def connection_status(func):
    @wraps(func)
    def connected_status(update: Update, context: CallbackContext, *args, **kwargs):
        conn = connected(
            context.bot,
            update,
            update.effective_chat,
            update.effective_user.id,
            need_admin=False,
        )

        if conn:
            chat = dispatcher.bot.getChat(conn)
            update.__setattr__("_effective_chat", chat)
        elif update.effective_message.chat.type == "private":
            update.effective_message.reply_text(
                "Send /connect in a group that you and I have in common first.",
            )
            return connected_status

        return func(update, context, *args, **kwargs)

    return connected_status

from scenario.modules import connection

connected = connection.connected
