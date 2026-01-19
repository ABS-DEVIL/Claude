from pyrogram import Client, idle
from bot.config import Config
import os
import sys

# Create downloads directory
os.makedirs(Config.STORAGE_PATH, exist_ok=True)

print("=" * 60)
print("🔥 ABS_Stream_Fucker Bot Initializing... 🔥")
print("=" * 60)

# Initialize bot with EXPLICIT handler loading
app = Client(
    name="abs_stream_fucker",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    workdir="/tmp"
)

async def main():
    """Main function with manual handler imports"""
    try:
        print("\n🚀 Starting bot...")
        
        # Start the bot FIRST
        await app.start()
        
        # Get bot info
        me = await app.get_me()
        
        print("\n" + "=" * 60)
        print("✅ BOT STARTED SUCCESSFULLY!")
        print("=" * 60)
        print(f"📱 Username: @{me.username}")
        print(f"🆔 Bot ID: {me.id}")
        print(f"👤 Name: {me.first_name}")
        print("=" * 60)
        
        # NOW manually import handlers after bot is started
        print("\n📦 Loading handlers...")
        
        try:
            from bot.handlers import start, files, links, admin, fsub
            print("✅ Handlers loaded: start, files, links, admin, fsub")
        except ImportError as e:
            print(f"⚠️ Some handlers missing: {e}")
            print("⚠️ Bot will run with basic functionality")
        
        print("\n" + "=" * 60)
        print(f"💬 Test now: Open @{me.username} and send /start")
        print("✅ Bot is LIVE and ready to accept commands!")
        print("=" * 60 + "\n")
        
        # Keep the bot running
        await idle()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        print("\n🛑 Stopping bot...")
        try:
            await app.stop()
            print("✅ Bot stopped gracefully")
        except:
            pass

if __name__ == "__main__":
    try:
        app.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
