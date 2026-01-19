from pyrogram import Client, filters
from pyrogram.types import Message
from bot.config import Config
import os

# Create downloads directory
os.makedirs(Config.STORAGE_PATH, exist_ok=True)

# Initialize bot
app = Client(
    name="abs_stream_fucker",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    workdir="/tmp"
)

# ==================== HANDLERS ====================

@app.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    """Start command handler"""
    user = message.from_user
    
    welcome_text = f"""
🔥 <b>Yo! Welcome to {Config.BOT_NAME}</b> 🔥

👤 <b>User:</b> {user.first_name}
🆔 <b>ID:</b> <code>{user.id}</code>

<b>Kya kar sakta hai tu:</b>
📤 File bhej → Stream + Download link mil jayega
🔗 Link bhej → Auto download karunga
🔐 Password protection laga sakta hai

<b>Commands:</b>
/start - Start bot
/help - Help menu

Ab file ya link bhej, bakchodi nahi 😎
"""
    
    await message.reply_text(welcome_text, quote=True)
    print(f"✅ /start from user {user.id} (@{user.username})")

@app.on_message(filters.command("help") & filters.private)
async def help_command(client: Client, message: Message):
    """Help command handler"""
    help_text = """
❓ <b>How to Use</b>

<b>1️⃣ Upload File:</b>
Just send any file → Get stream + download link

<b>2️⃣ Send Link:</b>
Send YouTube/Insta link → I'll download & give you links

<b>3️⃣ Commands:</b>
/start - Start bot
/help - This message

<b>Need Help?</b>
Contact: @{owner}
"""
    
    await message.reply_text(help_text.replace("{owner}", str(Config.OWNER_ID)), quote=True)

@app.on_message(filters.private & (filters.document | filters.video | filters.audio))
async def file_handler(client: Client, message: Message):
    """Handle file uploads"""
    user = message.from_user
    
    # Get file info
    if message.document:
        file_name = message.document.file_name
        file_size = message.document.file_size
    elif message.video:
        file_name = f"video_{message.video.file_unique_id}.mp4"
        file_size = message.video.file_size
    elif message.audio:
        file_name = message.audio.file_name or f"audio_{message.audio.file_unique_id}.mp3"
        file_size = message.audio.file_size
    else:
        return
    
    file_size_mb = file_size / (1024 * 1024)
    
    response = f"""
✅ <b>File Received!</b> 🔥

📁 <b>File:</b> <code>{file_name}</code>
📦 <b>Size:</b> {file_size_mb:.2f} MB

<b>Processing...</b>
Link generation coming soon! 🚀

<i>Full features will be available after complete setup</i>
"""
    
    await message.reply_text(response, quote=True)
    print(f"✅ File from user {user.id}: {file_name}")

@app.on_message(filters.private & filters.text & ~filters.command(["start", "help"]))
async def text_handler(client: Client, message: Message):
    """Handle random text"""
    user = message.from_user
    text = message.text
    
    # Check if it's a URL
    if text.startswith("http"):
        response = """
🔗 <b>Link Received!</b>

Download feature coming soon! 🚀

<i>Full leech functionality will be available after complete setup</i>
"""
    else:
        response = """
Bhai mujhe koi file ya link nahi mila 😑

File ya link bhej.
Bakchodi band kar laude 😡
"""
    
    await message.reply_text(response, quote=True)
    print(f"📝 Message from user {user.id}: {text[:50]}")

# ==================== MAIN ====================

async def main():
    """Main function"""
    try:
        print("=" * 60)
        print("🔥 ABS_Stream_Fucker Bot Starting... 🔥")
        print("=" * 60)
        
        await app.start()
        
        me = await app.get_me()
        
        print("\n✅ BOT STARTED SUCCESSFULLY!")
        print(f"📱 Username: @{me.username}")
        print(f"🆔 Bot ID: {me.id}")
        print(f"👤 Name: {me.first_name}")
        print(f"\n💬 Test: Open @{me.username} and send /start")
        print("✅ Bot is LIVE!\n")
        
        await app.idle()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await app.stop()

if __name__ == "__main__":
    app.run(main())
