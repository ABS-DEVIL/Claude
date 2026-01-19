from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot.config import Config
from bot.utils.database import db
from bot.utils.security import generate_token, generate_key, hash_password
from bot.utils.limits import check_file_limit, check_user_restrictions
from bot.utils.logger import log_to_channel
from bot.handlers.fsub import check_fsub, send_fsub_message
import asyncio

# Store password temp data
password_mode = {}

@Client.on_message(filters.private & (filters.document | filters.video | filters.audio))
async def file_handler(client: Client, message: Message):
    user_id = message.from_user.id
    
    # Check user restrictions
    can_use, error_msg = await check_user_restrictions(user_id)
    if not can_use:
        await message.reply_text(error_msg, quote=True)
        return
    
    # Check force subscribe
    is_joined, keyboard = await check_fsub(client, user_id)
    if not is_joined:
        await send_fsub_message(message, keyboard)
        return
    
    # Check file limit
    can_upload, error_msg = await check_file_limit(user_id)
    if not can_upload:
        await message.reply_text(
            f"{error_msg}\n\n"
            "Limit tod ke kya milega? 24 ghante wait kar ya Premium le 💰",
            quote=True
        )
        # Mute user for 24h
        await db.mute_user(user_id, 24)
        return
    
    # Get user info
    user = await db.get_user(user_id)
    is_premium = user.get("is_premium", False)
    
    # Wait time for free users
    if not is_premium:
        wait_msg = await message.reply_text(
            f"⏳ <b>Thoda wait kar bhai...</b>\n\n"
            f"Free users ke liye {Config.FREE_WAIT_TIME} seconds wait hai 😴\n"
            f"Premium le le instant access ke liye! 🚀",
            quote=True
        )
        await asyncio.sleep(Config.FREE_WAIT_TIME)
        await wait_msg.delete()
    
    # Processing message
    process_msg = await message.reply_text(
        "⚙️ <b>Processing ho raha hai tera file...</b> 🔥\n\n"
        "Wait kar, link bana raha hu 🔗",
        quote=True
    )
    
    try:
        # Get file info
        if message.document:
            file_id = message.document.file_id
            file_name = message.document.file_name
            file_size = message.document.file_size
            mime_type = message.document.mime_type
        elif message.video:
            file_id = message.video.file_id
            file_name = f"video_{message.video.file_unique_id}.mp4"
            file_size = message.video.file_size
            mime_type = message.video.mime_type
        elif message.audio:
            file_id = message.audio.file_id
            file_name = message.audio.file_name or f"audio_{message.audio.file_unique_id}.mp3"
            file_size = message.audio.file_size
            mime_type = message.audio.mime_type
        else:
            await process_msg.edit_text("❌ File type supported nahi hai bhai 😕")
            return
        
        # Check if user wants password
        password = None
        key = None
        
        # Add file to database
        file_data = {
            "file_id": file_id,
            "file_name": file_name,
            "file_size": file_size,
            "mime_type": mime_type,
            "password": password,
            "key": key,
            "is_premium": is_premium
        }
        
        file_doc = await db.add_file(user_id, file_data)
        token = file_doc["token"]
        
        # Increment file count
        await db.increment_file_count(user_id)
        
        # Generate URLs
        stream_url = f"{Config.WEB_URL}/stream/{token}"
        download_url = f"{Config.WEB_URL}/download/{token}"
        
        # Create response
        file_size_mb = file_size / (1024 * 1024)
        expiry_text = "1 year" if is_premium else "24 hours"
        
        response_text = f"""
✅ <b>File Upload Successfully!</b> 🔥

📁 <b>File:</b> <code>{file_name}</code>
📦 <b>Size:</b> {file_size_mb:.2f} MB
⏰ <b>Expiry:</b> {expiry_text}

🔗 <b>Your Links:</b>

📺 <b>Stream:</b>
<code>{stream_url}</code>

⬇️ <b>Download:</b>
<code>{download_url}</code>

<i>💡 Tip: Reply /password your_pass to add password protection</i>
"""
        
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📺 Stream Now", url=stream_url)],
            [InlineKeyboardButton("⬇️ Download", url=download_url)],
            [InlineKeyboardButton("🔐 Add Password", callback_data=f"add_pass_{token}")]
        ])
        
        await process_msg.edit_text(response_text, reply_markup=buttons)
        
        # Store in password mode for quick reply
        password_mode[user_id] = token
        
        # Log to channel
        details = f"File: {file_name}\nSize: {file_size_mb:.2f} MB\nStream: {stream_url}"
        await log_to_channel(client, "FILE_UPLOAD", user_id, details, message)
        
    except Exception as e:
        await process_msg.edit_text(
            f"❌ <b>Error aa gaya bhai!</b> 😭\n\n"
            f"Error: <code>{str(e)}</code>\n\n"
            "Dubara try kar ya owner ko bata"
        )
        print(f"File handler error: {e}")

@Client.on_message(filters.command("password") & filters.private)
async def password_handler(client: Client, message: Message):
    user_id = message.from_user.id
    
    # Check if replying to file message or has active token
    if not message.reply_to_message and user_id not in password_mode:
        await message.reply_text(
            "❌ <b>Reply kar file message pe ya recent uploaded file pe use kar</b>\n\n"
            "Usage: <code>/password your_password</code>",
            quote=True
        )
        return
    
    # Get password
    try:
        password = message.text.split(maxsplit=1)[1]
    except:
        await message.reply_text(
            "❌ <b>Password dena bhul gaya kya?</b> 😑\n\n"
            "Usage: <code>/password your_password</code>",
            quote=True
        )
        return
    
    # Get token
    token = password_mode.get(user_id)
    
    if not token:
        await message.reply_text(
            "❌ <b>Token nahi mila</b>\n\n"
            "Pehle file upload kar phir password set kar",
            quote=True
        )
        return
    
    # Hash password and update
    hashed = hash_password(password)
    await db.files.update_one(
        {"token": token},
        {"$set": {"password": hashed}}
    )
    
    # Generate key
    key = generate_key()
    await db.files.update_one(
        {"token": token},
        {"$set": {"key": key}}
    )
    
    await message.reply_text(
        f"✅ <b>Password set ho gaya!</b> 🔐\n\n"
        f"🔑 <b>Password:</b> <code>{password}</code>\n"
        f"🗝️ <b>Key:</b> <code>{key}</code>\n\n"
        "<i>Ab tera file password protected hai! 🔥</i>",
        quote=True
    )
    
    # Clear password mode
    if user_id in password_mode:
        del password_mode[user_id]
    
    # Log
    await log_to_channel(client, "PASSWORD_SET", user_id, f"Token: {token}")

@Client.on_callback_query(filters.regex(r"^add_pass_"))
async def add_password_callback(client: Client, callback_query):
    token = callback_query.data.split("_")[2]
    user_id = callback_query.from_user.id
    
    # Store token in password mode
    password_mode[user_id] = token
    
    await callback_query.message.reply_text(
        "🔐 <b>Password set karne ke liye:</b>\n\n"
        "Reply kar is message pe:\n"
        "<code>/password your_password</code>\n\n"
        "Example: <code>/password mera123</code>",
        quote=True
    )
    
    await callback_query.answer("Reply karo /password command se!")

# Handle random text
@Client.on_message(filters.private & filters.text & ~filters.command(["start", "password", "boss", "ui", "restart"]))
async def random_text_handler(client: Client, message: Message):
    # Check if it's a link (will be handled by links.py)
    if message.text.startswith("http"):
        return
    
    savage_replies = [
        "Bhai mujhe koi file ya link nahi mila 😑\nFile ya link bhej.\nBakchodi band kar laude 😡",
        "Kya bol raha hai tu? 🤨\nMujhe file chahiye ya link.\nBaatein band kar 😤",
        "Samajh nahi aa raha tujhe?\nFile bhej ya link bhej.\nBakwaas band kar 🙄",
        "Yeh kya bhej diya tune? 😕\nFile ya link bhej properly.\nTime waste mat kar 😠"
    ]
    
    import random
    reply = random.choice(savage_replies)
    
    await message.reply_text(reply, quote=True)
