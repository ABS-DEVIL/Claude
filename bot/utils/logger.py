from pyrogram import Client
from bot.config import Config
from bot.utils.database import db
from datetime import datetime

async def log_to_channel(client: Client, log_type: str, user_id: int, details: str = None, file_message=None):
    """Send log to log channel"""
    if not Config.LOG_CHANNEL:
        return
    
    user = await db.get_user(user_id)
    username = user.get("username", "N/A") if user else "N/A"
    premium = "✅ Premium" if user and user.get("is_premium") else "❌ Free"
    
    log_text = f"""
🔔 <b>{log_type.upper()}</b>

👤 <b>User:</b> {user_id}
📝 <b>Username:</b> @{username}
💎 <b>Status:</b> {premium}
🕒 <b>Time:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
"""
    
    if details:
        log_text += f"\n📋 <b>Details:</b>\n{details}"
    
    try:
        if file_message:
            # Forward file first
            forwarded = await client.forward_messages(
                chat_id=Config.LOG_CHANNEL,
                from_chat_id=file_message.chat.id,
                message_ids=file_message.id
            )
            # Reply with log info
            await client.send_message(
                chat_id=Config.LOG_CHANNEL,
                text=log_text,
                reply_to_message_id=forwarded.id
            )
        else:
            await client.send_message(
                chat_id=Config.LOG_CHANNEL,
                text=log_text
            )
        
        # Also save to database
        await db.add_log(log_type, user_id, details)
    except Exception as e:
        print(f"Failed to log: {e}")
