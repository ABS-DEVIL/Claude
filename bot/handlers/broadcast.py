from pyrogram import Client, filters
from pyrogram.types import Message
from bot.config import Config
from bot.utils.database import db
from bot.utils.logger import log_to_channel
import asyncio

# Store broadcast state
broadcast_state = {}

@Client.on_message(filters.command("broadcast") & filters.private)
async def broadcast_command(client: Client, message: Message):
    if message.from_user.id != Config.OWNER_ID:
        await message.reply_text("❌ Sirf owner use kar sakta hai bhai! 🚫", quote=True)
        return
    
    broadcast_text = """
📢 <b>BROADCAST SYSTEM</b>

<b>How to use:</b>
1. Reply to this message with your broadcast content
2. Can include text, media, buttons
3. I'll send to all users

<b>Stats will be shown after broadcast</b>

Reply kar ab! 👇
"""
    
    sent = await message.reply_text(broadcast_text, quote=True)
    broadcast_state[message.from_user.id] = {
        'waiting': True,
        'message_id': sent.id
    }

@Client.on_message(filters.private & filters.reply)
async def broadcast_reply(client: Client, message: Message):
    user_id = message.from_user.id
    
    if user_id not in broadcast_state or not broadcast_state[user_id].get('waiting'):
        return
    
    if user_id != Config.OWNER_ID:
        return
    
    # Confirm broadcast
    confirm_text = """
⚠️ <b>CONFIRM BROADCAST</b>

Yeh message sab users ko jayega!

<b>Ready?</b>
"""
    
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Yes, Send", callback_data="broadcast_confirm"),
            InlineKeyboardButton("❌ Cancel", callback_data="broadcast_cancel")
        ]
    ])
    
    await message.reply_text(confirm_text, reply_markup=buttons, quote=True)
    
    # Store broadcast message
    broadcast_state[user_id]['message'] = message
    broadcast_state[user_id]['waiting'] = False

@Client.on_callback_query(filters.regex("^broadcast_"))
async def broadcast_callback(client: Client, callback_query):
    if callback_query.from_user.id != Config.OWNER_ID:
        await callback_query.answer("Not authorized!", show_alert=True)
        return
    
    action = callback_query.data.split("_")[1]
    user_id = callback_query.from_user.id
    
    if action == "cancel":
        if user_id in broadcast_state:
            del broadcast_state[user_id]
        
        await callback_query.message.edit_text("❌ Broadcast cancelled!")
        await callback_query.answer()
        return
    
    if action == "confirm":
        await callback_query.message.edit_text("📤 Broadcasting... Please wait!")
        
        broadcast_msg = broadcast_state[user_id].get('message')
        
        if not broadcast_msg:
            await callback_query.message.edit_text("❌ Message not found!")
            return
        
        # Get all users
        users = await db.get_all_users()
        
        total = len(users)
        success = 0
        failed = 0
        blocked = 0
        
        progress_msg = await callback_query.message.reply_text(
            f"📊 Progress: 0/{total}\n✅ Success: 0\n❌ Failed: 0\n🚫 Blocked: 0"
        )
        
        for i, user in enumerate(users):
            try:
                # Copy message to user
                await broadcast_msg.copy(user['user_id'])
                success += 1
                await asyncio.sleep(0.05)  # Rate limit protection
            except Exception as e:
                error_str = str(e).lower()
                if 'blocked' in error_str or 'deleted' in error_str:
                    blocked += 1
                else:
                    failed += 1
            
            # Update progress every 50 users
            if (i + 1) % 50 == 0 or (i + 1) == total:
                try:
                    await progress_msg.edit_text(
                        f"📊 Progress: {i+1}/{total}\n"
                        f"✅ Success: {success}\n"
                        f"❌ Failed: {failed}\n"
                        f"🚫 Blocked: {blocked}"
                    )
                except:
                    pass
        
        # Final report
        final_text = f"""
✅ <b>BROADCAST COMPLETE!</b>

📊 <b>Statistics:</b>
👥 Total Users: {total}
✅ Delivered: {success}
❌ Failed: {failed}
🚫 Blocked: {blocked}

<b>Success Rate: {(success/total*100):.1f}%</b>
"""
        
        await progress_msg.edit_text(final_text)
        
        # Log
        await log_to_channel(
            client,
            "BROADCAST",
            user_id,
            f"Total: {total}, Success: {success}, Failed: {failed}, Blocked: {blocked}"
        )
        
        # Clean up
        if user_id in broadcast_state:
            del broadcast_state[user_id]
        
        await callback_query.answer("Broadcast complete! 🎉")

@Client.on_message(filters.command("stats") & filters.private)
async def bot_stats(client: Client, message: Message):
    if message.from_user.id != Config.OWNER_ID:
        await message.reply_text("❌ Sirf owner dekh sakta hai! 🚫", quote=True)
        return
    
    # Get statistics
    total_users = await db.users.count_documents({})
    premium_users = await db.users.count_documents({"is_premium": True})
    banned_users = await db.users.count_documents({"is_banned": True})
    muted_users = await db.users.count_documents({"is_muted": True})
    
    total_files = await db.files.count_documents({})
    total_views = sum([f.get("views", 0) for f in await db.files.find().to_list(None)])
    total_downloads = sum([f.get("downloads", 0) for f in await db.files.find().to_list(None)])
    
    # Get today's stats
    from datetime import datetime
    today = datetime.utcnow().date().isoformat()
    today_users = await db.users.count_documents({"last_reset": today})
    
    stats_text = f"""
📊 <b>BOT STATISTICS</b>

👥 <b>Users:</b>
• Total: {total_users}
• Premium: {premium_users}
• Banned: {banned_users}
• Muted: {muted_users}
• Active Today: {today_users}

📁 <b>Files:</b>
• Total Uploaded: {total_files}
• Total Views: {total_views}
• Total Downloads: {total_downloads}

💎 <b>Premium Ratio:</b>
{(premium_users/total_users*100):.1f}% Premium Users

📈 <b>Engagement:</b>
Avg Views/File: {total_views/total_files if total_files > 0 else 0:.1f}
Avg Downloads/File: {total_downloads/total_files if total_files > 0 else 0:.1f}
"""
    
    await message.reply_text(stats_text, quote=True)
    
    # Log
    await log_to_channel(client, "STATS_VIEWED", message.from_user.id, stats_text)
