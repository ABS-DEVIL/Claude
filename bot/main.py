from pyrogram import Client, idle
from bot.config import Config
import os
import asyncio
import sys

# Create downloads directory
os.makedirs(Config.STORAGE_PATH, exist_ok=True)

print("=" * 60)
print("🔥 ABS_Stream_Fucker Bot Initializing... 🔥")
print("=" * 60)

# Initialize bot
app = Client(
    "abs_stream_fucker",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    plugins=dict(root="bot.handlers"),
    workdir="/tmp",  # Use /tmp for Heroku
    in_memory=False  # Save session to disk
)

async def main():
    """Main function to run the bot"""
    try:
        print("\n🚀 Starting bot...")
        
        # Start the bot
        await app.start()
        
        # Get bot info
        me = await app.get_me()
        
        print("\n" + "=" * 60)
        print("✅ BOT STARTED SUCCESSFULLY!")
        print("=" * 60)
        print(f"📱 Username: @{me.username}")
        print(f"🆔 Bot ID: {me.id}")
        print(f"👤 Name: {me.first_name}")
        print(f"🌐 DC ID: {me.dc_id}")
        print("=" * 60)
        print(f"\n💬 Test now: Open @{me.username} and send /start")
        print("\n✅ Bot is LIVE and ready to accept commands!\n")
        
        # Keep the bot running
        await idle()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\n⚠️ Common fixes:")
        print("1. Check BOT_TOKEN is correct")
        print("2. Verify API_ID and API_HASH")
        print("3. Ensure MongoDB is accessible")
        sys.exit(1)
    
    finally:
        print("\n🛑 Stopping bot...")
        await app.stop()
        print("✅ Bot stopped")

if __name__ == "__main__":
    try:
        # Run the bot
        app.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
