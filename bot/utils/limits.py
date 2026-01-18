from bot.config import Config
from bot.utils.database import db

async def check_file_limit(user_id):
    user = await db.get_user(user_id)
    if not user:
        return False, "User not found"
    
    if user.get("is_premium"):
        return True, None
    
    if user.get("daily_files", 0) >= Config.FREE_FILE_LIMIT:
        return False, f"Bhai tu aaj ke {Config.FREE_FILE_LIMIT} files already upload kar chuka hai 😑\n24 ghante baad aana ya Premium le le 🔥"
    
    return True, None

async def check_link_limit(user_id):
    user = await db.get_user(user_id)
    if not user:
        return False, "User not found"
    
    if user.get("is_premium"):
        return True, None
    
    if user.get("daily_links", 0) >= Config.FREE_LINK_LIMIT:
        return False, f"Bhai tu aaj ke {Config.FREE_LINK_LIMIT} links already generate kar chuka hai 😤\n24 ghante baad aana ya Premium kharid le 💰"
    
    return True, None

async def check_user_restrictions(user_id):
    user = await db.get_user(user_id)
    if not user:
        return False, "User not found bhai 🤔"
    
    if user.get("is_banned"):
        return False, "Tu banned hai bhai 🚫\nOwner se baat kar @YourOwnerUsername"
    
    if await db.check_mute_status(user_id):
        return False, "Tu 24 ghante ke liye mute hai 🔇\nLimit tod diya tha na? Ab wait kar 😏"
    
    return True, None
