from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot.config import Config
from bot.utils.database import db
from bot.utils.limits import check_link_limit, check_user_restrictions
from bot.utils.logger import log_to_channel
from bot.utils.leech import leecher
from bot.handlers.fsub import check_fsub, send_fsub_message
import asyncio
import os

@Client.on_message(filters.private & filters.text & filters.regex(r"^https?://"))
async def link_handler(client: Client, message: Message):
    user_id = message.from_user.id
    url = message.text.strip()
    
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
    
    # Check link limit
    can_generate, error_msg = await check_link_limit(user_id)
    if not can_generate:
        await message.reply_text(
            f"{error_msg}\n\n"
            "Limit cross karne ki koshish? 😏\n24h wait kar ya Premium le!",
            quote=True
        )
        # Mute user for 24h
        await db.mute_user(user_id, 24)
        return
    
    # Get user info
    user = await db.get_user(user_id)
    is_premium = user.get("is_premium", False)
    
    # Detect site
    site = await leecher.detect_site(url)
    
    if not site:
        await message.reply_text(
            "❌ <b>Yeh link supported nahi hai bhai!</b> 😕\n\n"
            f"<b>Supported sites:</b>\n" + 
            "\n".join([f"• {s}" for s in Config.LEECH_SITES]),
            quote=True
        )
        return
    
    # Wait time for free users
    if not is_premium:
        wait_msg = await message.reply_text(
            f"⏳ <b>Wait kar bhai...</b>\n\n"
            f"{Config.FREE_WAIT_TIME} seconds ka wait hai 😴",
            quote=True
        )
        await asyncio.sleep(Config.FREE_WAIT_TIME)
        await wait_msg.delete()
    
    # Start downloading
    progress_msg = await message.reply_text(
        f"📥 <b>Download shuru ho gaya!</b>\n\n"
        f"🌐 <b>Site:</b> {site}\n"
        f"🔗 <b>URL:</b> <code>{url[:50]}...</code>\n\n"
        f"⏳ <b>Status:</b> Initializing...",
        quote=True
    )
    
    # Progress callback
    last_update = [0]
    async def progress_callback(downloaded, total, percentage):
        current_time = asyncio.get_event_loop().time()
        if current_time - last_update[0] < 2:  # Update every 2 seconds
            return
        last_update[0] = current_time
        
        downloaded_mb = downloaded / (1024 * 1024)
        total_mb = total / (1024 * 1024)
        
        progress_bar = "█" * int(percentage / 10) + "░" * (10 - int(percentage / 10))
        
        try:
            await progress_msg.edit_text(
                f"📥 <b>Downloading...</b>\n\n"
                f"📦 <b>Size:</b> {total_mb:.2f} MB\n"
                f"⬇️ <b>Downloaded:</b> {downloaded_mb:.2f} MB\n"
                f"📊 <b>Progress:</b> {percentage:.1f}%\n\n"
                f"[{progress_bar}]\n\n"
                f"⏳ Please wait..."
            )
        except:
            pass
    
    try:
        # Download file
        result = await leecher.download_from_url(url, progress_callback)
        
        if not result.get('success'):
            await progress_msg.edit_text(
                f"❌ <b>Download fail ho gaya!</b> 😭\n\n"
                f"Error: <code>{result.get('error')}</code>\n\n"
                "Link check kar ya dubara try kar"
            )
            return
        
        # Upload to Telegram
        await progress_msg.edit_text(
            "⬆️ <b>Telegram pe upload ho raha hai...</b>\n\n"
            "Wait kar, almost done! 🔥"
        )
        
        filepath = result.get('filename')
        filename = os.path.basename(filepath)
        filesize = result.get('size', 0)
        
        # Upload to log channel
        sent_file = await client.send_document(
            chat_id=Config.LOG_CHANNEL,
            document=filepath,
            caption=f"📁 Downloaded from {site}\n👤 User: {user_id}"
        )
        
        # Ask user if they want file
        ask_msg = await progress_msg.edit_text(
            f"✅ <b>Download complete!</b> 🎉\n\n"
            f"📁 <b>File:</b> <code>{filename}</code>\n"
            f"📦 <b>Size:</b> {filesize / (1024*1024):.2f} MB\n\n"
            f"<b>Tujhe Telegram file chahiye?</b>",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Yes, Send File", callback_data=f"send_file_{sent_file.id}")],
                [InlineKeyboardButton("❌ No, Just Links", callback_data=f"skip_file_{sent_file.id}")]
            ])
        )
        
        # Store file info for callback
        await db.files.update_one(
            {"_id": sent_file.id},
            {"$set": {
                "temp_file_id": sent_file.id,
                "temp_user_id": user_id,
                "temp_filepath": filepath,
                "temp_filename": filename,
                "temp_filesize": filesize
            }},
            upsert=True
        )
        
        # Increment link count
        await db.increment_link_count(user_id)
        
        # Log
        details = f"URL: {url}\nSite: {site}\nFile: {filename}"
        await log_to_channel(client, "LINK_DOWNLOAD", user_id, details)
        
    except Exception as e:
        await progress_msg.edit_text(
            f"❌ <b>Error aa gaya bhai!</b> 😭\n\n"
            f"Error: <code>{str(e)}</code>\n\n"
            "Dubara try kar"
        )
        print(f"Link handler error: {e}")

@Client.on_callback_query(filters.regex(r"^send_file_"))
async def send_file_callback(client: Client, callback_query):
    file_id = int(callback_query.data.split("_")[2])
    user_id = callback_query.from_user.id
    
    # Get file info
    file_info = await db.files.find_one({"temp_file_id": file_id})
    
    if not file_info or file_info.get("temp_user_id") != user_id:
        await callback_query.answer("File not found or unauthorized!", show_alert=True)
        return
    
    try:
        # Forward file from log channel
        await client.copy_message(
            chat_id=user_id,
            from_chat_id=Config.LOG_CHANNEL,
            message_id=file_id
        )
        
        # Now generate stream links
        await generate_and_send_links(client, callback_query.message, file_info, user_id)
        
        await callback_query.answer("File sent! Links generated 🔥")
        
    except Exception as e:
        await callback_query.answer(f"Error: {str(e)}", show_alert=True)

@Client.on_callback_query(filters.regex(r"^skip_file_"))
async def skip_file_callback(client: Client, callback_query):
    file_id = int(callback_query.data.split("_")[2])
    user_id = callback_query.from_user.id
    
    # Get file info
    file_info = await db.files.find_one({"temp_file_id": file_id})
    
    if not file_info or file_info.get("temp_user_id") != user_id:
        await callback_query.answer("File not found or unauthorized!", show_alert=True)
        return
    
    # Generate stream links
    await generate_and_send_links(client, callback_query.message, file_info, user_id)
    
    await callback_query.answer("Links generated! 🔗")

async def generate_and_send_links(client, message, file_info, user_id):
    """Generate stream and download links"""
    user = await db.get_user(user_id)
    is_premium = user.get("is_premium", False)
    
    # Add file to database
    file_data = {
        "file_id": file_info.get("temp_file_id"),
        "file_name": file_info.get("temp_filename"),
        "file_size": file_info.get("temp_filesize"),
        "mime_type": "application/octet-stream",
        "password": None,
        "key": None,
        "is_premium": is_premium
    }
    
    file_doc = await db.add_file(user_id, file_data)
    token = file_doc["token"]
    
    # Generate URLs
    stream_url = f"{Config.WEB_URL}/stream/{token}"
    download_url = f"{Config.WEB_URL}/download/{token}"
    
    # Response
    file_size_mb = file_info.get("temp_filesize", 0) / (1024 * 1024)
    expiry_text = "1 year" if is_premium else "24 hours"
    
    response_text = f"""
✅ <b>Links Generated!</b> 🔥

📁 <b>File:</b> <code>{file_info.get("temp_filename")}</code>
📦 <b>Size:</b> {file_size_mb:.2f} MB
⏰ <b>Expiry:</b> {expiry_text}

🔗 <b>Your Links:</b>

📺 <b>Stream:</b>
<code>{stream_url}</code>

⬇️ <b>Download:</b>
<code>{download_url}</code>
"""
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📺 Stream Now", url=stream_url)],
        [InlineKeyboardButton("⬇️ Download", url=download_url)]
    ])
    
    await message.edit_text(response_text, reply_markup=buttons)
    
    # Clean up temp file
    try:
        filepath = file_info.get("temp_filepath")
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
    except:
        pass
