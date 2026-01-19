from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot.config import Config
from bot.utils.database import db
from bot.utils.logger import log_to_channel
import sys
import os

def is_admin(user_id):
    return user_id == Config.OWNER_ID

@Client.on_message(filters.command("boss") & filters.private)
async def boss_panel(client: Client, message: Message):
    if not is_admin(message.from_user.id):
        await message.reply_text("❌ Tu admin nahi hai bhai! 🚫", quote=True)
        return
    
    admin_text = f"""
👑 <b>BOSS PANEL</b> 👑

Welcome back, boss! 🔥

<b>What do you want to do?</b>
Choose from the options below:
"""
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("👥 User Management", callback_data="admin_users")],
        [InlineKeyboardButton("📊 Statistics", callback_data="admin_stats")],
        [InlineKeyboardButton("🔔 Force Subscribe", callback_data="admin_fsub")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="admin_settings")],
        [InlineKeyboardButton("🔄 Restart Bot", callback_data="admin_restart")],
        [InlineKeyboardButton("📝 Logs", callback_data="admin_logs")]
    ])
    
    await message.reply_text(admin_text, reply_markup=buttons, quote=True)

@Client.on_message(filters.command("ui") & filters.private)
async def user_info(client: Client, message: Message):
    if not is_admin(message.from_user.id):
        await message.reply_text("❌ Tu admin nahi hai bhai! 🚫", quote=True)
        return
    
    try:
        # Get user ID or username
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.reply_text(
                "Usage: <code>/ui user_id</code> or <code>/ui @username</code>",
                quote=True
            )
            return
        
        target = args[1]
        
        # Check if it's ID or username
        if target.isdigit():
            user_id = int(target)
            user_data = await db.get_user(user_id)
        else:
            username = target.replace("@", "")
            user_data = await db.users.find_one({"username": username})
        
        if not user_data:
            await message.reply_text("❌ User not found!", quote=True)
            return
        
        user_id = user_data.get("user_id")
        username = user_data.get("username", "N/A")
        is_premium = user_data.get("is_premium", False)
        is_banned = user_data.get("is_banned", False)
        is_muted = user_data.get("is_muted", False)
        daily_files = user_data.get("daily_files", 0)
        daily_links = user_data.get("daily_links", 0)
        joined_at = user_data.get("joined_at", "N/A")
        
        # Get file count
        file_count = await db.files.count_documents({"user_id": user_id})
        
        info_text = f"""
👤 <b>USER INFO</b>

🆔 <b>ID:</b> <code>{user_id}</code>
📝 <b>Username:</b> @{username}
💎 <b>Premium:</b> {"✅ Yes" if is_premium else "❌ No"}
🚫 <b>Banned:</b> {"✅ Yes" if is_banned else "❌ No"}
🔇 <b>Muted:</b> {"✅ Yes" if is_muted else "❌ No"}

<b>Today's Usage:</b>
📤 <b>Files:</b> {daily_files}/{Config.FREE_FILE_LIMIT}
🔗 <b>Links:</b> {daily_links}/{Config.FREE_LINK_LIMIT}

<b>Total Stats:</b>
📁 <b>Total Files:</b> {file_count}
📅 <b>Joined:</b> {joined_at}
"""
        
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🚫 Ban", callback_data=f"ban_{user_id}"),
                InlineKeyboardButton("✅ Unban", callback_data=f"unban_{user_id}")
            ],
            [
                InlineKeyboardButton("🔇 Mute 24h", callback_data=f"mute_{user_id}"),
                InlineKeyboardButton("🔊 Unmute", callback_data=f"unmute_{user_id}")
            ],
            [
                InlineKeyboardButton("💎 Add Premium", callback_data=f"premium_add_{user_id}"),
                InlineKeyboardButton("❌ Remove Premium", callback_data=f"premium_remove_{user_id}")
            ],
            [InlineKeyboardButton("🔄 Refresh", callback_data=f"refresh_ui_{user_id}")]
        ])
        
        await message.reply_text(info_text, reply_markup=buttons, quote=True)
        
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}", quote=True)

# Admin callbacks
@Client.on_callback_query(filters.regex("^admin_"))
async def admin_callbacks(client: Client, callback_query: CallbackQuery):
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("Not authorized!", show_alert=True)
        return
    
    action = callback_query.data
    
    # User Management
    if action == "admin_users":
        total_users = await db.users.count_documents({})
        premium_users = await db.users.count_documents({"is_premium": True})
        banned_users = await db.users.count_documents({"is_banned": True})
        muted_users = await db.users.count_documents({"is_muted": True})
        
        text = f"""
👥 <b>USER MANAGEMENT</b>

📊 <b>Statistics:</b>
• Total Users: {total_users}
• Premium Users: {premium_users}
• Banned Users: {banned_users}
• Muted Users: {muted_users}

Use /ui <user_id> to manage specific users
"""
        
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ Back", callback_data="back_to_boss")]
        ])
        
        await callback_query.message.edit_text(text, reply_markup=buttons)
    
    # Statistics
    elif action == "admin_stats":
        total_users = await db.users.count_documents({})
        total_files = await db.files.count_documents({})
        total_views = sum([f.get("views", 0) for f in await db.files.find().to_list(None)])
        total_downloads = sum([f.get("downloads", 0) for f in await db.files.find().to_list(None)])
        
        text = f"""
📊 <b>STATISTICS</b>

👥 <b>Users:</b> {total_users}
📁 <b>Files:</b> {total_files}
👁️ <b>Total Views:</b> {total_views}
⬇️ <b>Total Downloads:</b> {total_downloads}

<b>Performance:</b>
🚀 Bot is running smoothly!
"""
        
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Refresh", callback_data="admin_stats")],
            [InlineKeyboardButton("◀️ Back", callback_data="back_to_boss")]
        ])
        
        await callback_query.message.edit_text(text, reply_markup=buttons)
    
    # Force Subscribe
    elif action == "admin_fsub":
        fsub_channels = await db.get_all_fsub()
        
        if fsub_channels:
            channels_text = "\n".join([f"• {c.get('channel_name')} (<code>{c.get('channel_id')}</code>)" for c in fsub_channels])
        else:
            channels_text = "No channels added yet"
        
        text = f"""
🔔 <b>FORCE SUBSCRIBE</b>

<b>Current Channels:</b>
{channels_text}

<b>Commands:</b>
• Add: <code>/addfsub channel_id channel_name</code>
• Remove: <code>/rmfsub channel_id</code>
"""
        
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ Back", callback_data="back_to_boss")]
        ])
        
        await callback_query.message.edit_text(text, reply_markup=buttons)
    
    # Settings
    elif action == "admin_settings":
        text = f"""
⚙️ <b>SETTINGS</b>

<b>Free User Limits:</b>
• Daily Files: {Config.FREE_FILE_LIMIT}
• Daily Links: {Config.FREE_LINK_LIMIT}
• Wait Time: {Config.FREE_WAIT_TIME}s
• Expiry: {Config.FREE_EXPIRY / 3600} hours

<b>Premium Settings:</b>
• Wait Time: {Config.PREMIUM_WAIT_TIME}s
• Expiry: {Config.PREMIUM_EXPIRY / (3600 * 24)} days

<i>Edit config.py to change settings</i>
"""
        
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ Back", callback_data="back_to_boss")]
        ])
        
        await callback_query.message.edit_text(text, reply_markup=buttons)
    
    # Restart
    elif action == "admin_restart":
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Confirm Restart", callback_data="confirm_restart")],
            [InlineKeyboardButton("❌ Cancel", callback_data="back_to_boss")]
        ])
        
        await callback_query.message.edit_text(
            "⚠️ <b>Are you sure you want to restart the bot?</b>",
            reply_markup=buttons
        )
    
    # Logs
    elif action == "admin_logs":
        recent_logs = await db.logs.find().sort("timestamp", -1).limit(10).to_list(None)
        
        if recent_logs:
            logs_text = ""
            for log in recent_logs:
                logs_text += f"• {log.get('type')} - User {log.get('user_id')} - {log.get('timestamp')}\n"
        else:
            logs_text = "No logs yet"
        
        text = f"""
📝 <b>RECENT LOGS</b>

{logs_text}

<i>Check log channel for detailed logs</i>
"""
        
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Refresh", callback_data="admin_logs")],
            [InlineKeyboardButton("◀️ Back", callback_data="back_to_boss")]
        ])
        
        await callback_query.message.edit_text(text, reply_markup=buttons)
    
    await callback_query.answer()

@Client.on_callback_query(filters.regex("^back_to_boss$"))
async def back_to_boss(client: Client, callback_query: CallbackQuery):
    admin_text = f"""
👑 <b>BOSS PANEL</b> 👑

Welcome back, boss! 🔥

<b>What do you want to do?</b>
Choose from the options below:
"""
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("👥 User Management", callback_data="admin_users")],
        [InlineKeyboardButton("📊 Statistics", callback_data="admin_stats")],
        [InlineKeyboardButton("🔔 Force Subscribe", callback_data="admin_fsub")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="admin_settings")],
        [InlineKeyboardButton("🔄 Restart Bot", callback_data="admin_restart")],
        [InlineKeyboardButton("📝 Logs", callback_data="admin_logs")]
    ])
    
    await callback_query.message.edit_text(admin_text, reply_markup=buttons)
    await callback_query.answer()

# User action callbacks
@Client.on_callback_query(filters.regex("^(ban|unban|mute|unmute|premium_add|premium_remove|refresh_ui)_"))
async def user_action_callbacks(client: Client, callback_query: CallbackQuery):
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("Not authorized!", show_alert=True)
        return
    
    action_data = callback_query.data.split("_")
    action = action_data[0]
    
    if action == "premium":
        action = f"{action_data[0]}_{action_data[1]}"
        user_id = int(action_data[2])
    elif action == "refresh":
        user_id = int(action_data[2])
    else:
        user_id = int(action_data[1])
    
    if action == "ban":
        await db.ban_user(user_id)
        await callback_query.answer("User banned! 🚫", show_alert=True)
        await log_to_channel(client, "USER_BANNED", user_id, f"Banned by admin")
    
    elif action == "unban":
        await db.unban_user(user_id)
        await callback_query.answer("User unbanned! ✅", show_alert=True)
        await log_to_channel(client, "USER_UNBANNED", user_id, f"Unbanned by admin")
    
    elif action == "mute":
        await db.mute_user(user_id, 24)
        await callback_query.answer("User muted for 24h! 🔇", show_alert=True)
        await log_to_channel(client, "USER_MUTED", user_id, f"Muted by admin")
    
    elif action == "unmute":
        await db.unmute_user(user_id)
        await callback_query.answer("User unmuted! 🔊", show_alert=True)
        await log_to_channel(client, "USER_UNMUTED", user_id, f"Unmuted by admin")
    
    elif action == "premium_add":
        await db.set_premium(user_id, True)
        await callback_query.answer("Premium added! 💎", show_alert=True)
        await log_to_channel(client, "PREMIUM_ADDED", user_id, f"Premium added by admin")
    
    elif action == "premium_remove":
        await db.set_premium(user_id, False)
        await callback_query.answer("Premium removed! ❌", show_alert=True)
        await log_to_channel(client, "PREMIUM_REMOVED", user_id, f"Premium removed by admin")
    
    # Refresh UI
    if action == "refresh" or action in ["ban", "unban", "mute", "unmute", "premium_add", "premium_remove"]:
        user_data = await db.get_user(user_id)
        username = user_data.get("username", "N/A")
        is_premium = user_data.get("is_premium", False)
        is_banned = user_data.get("is_banned", False)
        is_muted = user_data.get("is_muted", False)
        daily_files = user_data.get("daily_files", 0)
        daily_links = user_data.get("daily_links", 0)
        joined_at = user_data.get("joined_at", "N/A")
        file_count = await db.files.count_documents({"user_id": user_id})
        
        info_text = f"""
👤 <b>USER INFO</b>

🆔 <b>ID:</b> <code>{user_id}</code>
📝 <b>Username:</b> @{username}
💎 <b>Premium:</b> {"✅ Yes" if is_premium else "❌ No"}
🚫 <b>Banned:</b> {"✅ Yes" if is_banned else "❌ No"}
🔇 <b>Muted:</b> {"✅ Yes" if is_muted else "❌ No"}

<b>Today's Usage:</b>
📤 <b>Files:</b> {daily_files}/{Config.FREE_FILE_LIMIT}
🔗 <b>Links:</b> {daily_links}/{Config.FREE_LINK_LIMIT}

<b>Total Stats:</b>
📁 <b>Total Files:</b> {file_count}
📅 <b>Joined:</b> {joined_at}
"""
        
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🚫 Ban", callback_data=f"ban_{user_id}"),
                InlineKeyboardButton("✅ Unban", callback_data=f"unban_{user_id}")
            ],
            [
                InlineKeyboardButton("🔇 Mute 24h", callback_data=f"mute_{user_id}"),
                InlineKeyboardButton("🔊 Unmute", callback_data=f"unmute_{user_id}")
            ],
            [
                InlineKeyboardButton("💎 Add Premium", callback_data=f"premium_add_{user_id}"),
                InlineKeyboardButton("❌ Remove Premium", callback_data=f"premium_remove_{user_id}")
            ],
            [InlineKeyboardButton("🔄 Refresh", callback_data=f"refresh_ui_{user_id}")]
        ])
        
        await callback_query.message.edit_text(info_text, reply_markup=buttons)

@Client.on_callback_query(filters.regex("^confirm_restart$"))
async def confirm_restart(client: Client, callback_query: CallbackQuery):
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("Not authorized!", show_alert=True)
        return
    
    await callback_query.message.edit_text("🔄 <b>Restarting bot...</b>")
    await callback_query.answer()
    
    await log_to_channel(client, "BOT_RESTART", callback_query.from_user.id, "Manual restart by admin")
    
    # Restart
    os.execl(sys.executable, sys.executable, *sys.argv)

# Force Subscribe Management
@Client.on_message(filters.command("addfsub") & filters.private)
async def add_fsub(client: Client, message: Message):
    if not is_admin(message.from_user.id):
        await message.reply_text("❌ Not authorized!", quote=True)
        return
    
    try:
        args = message.text.split(maxsplit=2)
        if len(args) < 3:
            await message.reply_text(
                "Usage: <code>/addfsub channel_id channel_name</code>\n\n"
                "Example: <code>/addfsub -1001234567890 My Channel</code>",
                quote=True
            )
            return
        
        channel_id = int(args[1])
        channel_name = args[2]
        
        await db.add_fsub(channel_id, channel_name)
        
        await message.reply_text(
            f"✅ Force Subscribe added!\n\n"
            f"Channel: {channel_name}\n"
            f"ID: <code>{channel_id}</code>",
            quote=True
        )
        
        await log_to_channel(client, "FSUB_ADDED", message.from_user.id, f"Channel: {channel_name}")
        
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}", quote=True)

@Client.on_message(filters.command("rmfsub") & filters.private)
async def remove_fsub(client: Client, message: Message):
    if not is_admin(message.from_user.id):
        await message.reply_text("❌ Not authorized!", quote=True)
        return
    
    try:
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text(
                "Usage: <code>/rmfsub channel_id</code>",
                quote=True
            )
            return
        
        channel_id = int(args[1])
        
        await db.remove_fsub(channel_id)
        
        await message.reply_text(
            f"✅ Force Subscribe removed!\n\n"
            f"Channel ID: <code>{channel_id}</code>",
            quote=True
        )
        
        await log_to_channel(client, "FSUB_REMOVED", message.from_user.id, f"Channel ID: {channel_id}")
        
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}", quote=True)
